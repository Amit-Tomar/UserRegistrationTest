from flask import Flask, jsonify, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from validate_email import validate_email

import os, jwt, traceback, datetime

TIME_TO_LIVE = 300

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(os.path.dirname(__file__),'database', 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)

if app.config['SECRET_KEY'] is None:
	raise EnvironmentError('Secret key could not be extracted from environment')

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	user_name = db.Column(db.String(64))
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(64), unique=True, index=True)

	def __init__(self, user_name, email, password):
		self.email = email
		self.password = password
		self.user_name = user_name

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User %r>' % self.user_name

	def encode_auth_token(self):
		try:
			print 'Encoded ' + str(self.id)
			payload = {
				'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=TIME_TO_LIVE),
				'iat': datetime.datetime.utcnow(),
				'sub': self.id
			}
			return jwt.encode(
				payload,
				app.config.get('SECRET_KEY'),
				algorithm='HS256'
			)
		except:
			traceback.print_exc()
			raise Exception("Could not generate auth token")

	@staticmethod
	def decode_auth_token(auth_token):
		try:
			payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
			return payload['sub']
		except jwt.ExpiredSignatureError:
			return 'Signature expired. Please log in again.'
		except jwt.InvalidTokenError:
			return 'Invalid token. Please log in again.'

def validatePassword(password):
	if not password or len(password) < 8:
		return False
	else:
		return True


@app.route('/', methods=['GET'])
def default():
	return "Server is up and running."

@app.route('/users/signup/', methods=['POST'])
def register():
	post_data = request.get_json()
	print post_data
	if (not post_data.get('user_name')) or (not post_data.get('password')) or (not post_data.get('email')):
		return jsonify({"message" : "UserName/Password/Email can not be empty"}), 422

	if not validatePassword(post_data.get('password')):
		return jsonify({"message": "Password should be atleast of 8 characters"}), 422

	if not validate_email(post_data.get('email')):
		return jsonify({"message": "Invalid e-mail ID"}), 422

	user = User.query.filter_by(email=post_data.get('email')).first()

	if user is not None:
		return jsonify({"message": "User already exists"}), 422
	else:
		user = User( email=post_data.get('email'),password=post_data.get('password'), user_name=post_data.get('user_name') )
		db.session.add(user)
		db.session.flush()
		try:
			auth_token = user.encode_auth_token()
		except:
			return jsonify({"message": "Auth token could not be generated"}), 500

		db.session.commit()

		return jsonify({"message": "User registered sucessfully","auth_token" : auth_token.decode()}), 200

@app.route('/users/signin/', methods=['POST'])
def login():
	post_data = request.get_json()
	print post_data
	if (not post_data.get('password')) or (not post_data.get('email')):
		return jsonify({"message": "Password/Email can not be empty"}), 422

	if not validate_email(post_data.get('email')):
		return jsonify({"message": "Invalid e-mail ID"}), 422

	user = User.query.filter_by(email=post_data.get('email')).first()

	if user and user.verify_password(post_data.get('password')):
		try:
			auth_token = user.encode_auth_token()
		except:
			return jsonify({"message": "Auth token could not be generated"}), 500

		return jsonify({"message": "User logged in sucessfully", "auth_token": auth_token.decode()}), 200
	else:
		return jsonify({"message": "User is not registered or password is incorrect"}), 200

@app.route('/users/profile/', methods=['GET','PATCH'])
def user_profile():
	if request.method == 'GET':
		auth_header = request.headers.get('Authorization')
		if auth_header and " " in auth_header:
			auth_token = auth_header.split(" ")[1]
		else:
			auth_token = ''

		if auth_token:
			user_id_from_token = User.decode_auth_token(auth_token)

			if not isinstance(user_id_from_token, str):
				user = User.query.filter_by(id=user_id_from_token).first()

				if user:
					responseObject = {
						'status': 'success',
						'data': {
							'id': user.id,
							'email': user.email,
							'user_name': user.user_name,
						}
					}
					return jsonify(responseObject), 200
				else:
					return jsonify({"message": "User ID does not exist"}), 500
			else:
				return jsonify({"message": "Auth Failed : " + str(user_id_from_token) }), 401
		else:
			return jsonify({"message": "Invalid Token"}), 401

	elif request.method == 'PATCH':
		patch_data = request.get_json()
		auth_header = request.headers.get('Authorization')
		if auth_header and " " in auth_header:
			auth_token = auth_header.split(" ")[1]
		else:
			auth_token = ''

		if auth_token:
			user_id_from_token = User.decode_auth_token(auth_token)

			if not isinstance(user_id_from_token, str):
				user = User.query.filter_by(id=user_id_from_token).first()
				if user:
					if patch_data.get('user_name'):
						user.user_name = patch_data.get('user_name')
					if patch_data.get('password'):
						user.password = patch_data.get('password')

					if not validatePassword(patch_data.get('password')):
						return jsonify({"message": "Password should be atleast of 8 characters"}), 422

					db.session.commit()

					responseObject = {
						'status': 'success',
						'data': {
							'id': user.id,
							'email': user.email,
							'user_name': user.user_name,
						}
					}
					return jsonify(responseObject), 200
				else:
					return jsonify({"message": "User ID does not exist"}), 500
			else:
				return jsonify({"message": "Auth Failed : " + str(user_id_from_token)}), 401
		else:
			return jsonify({"message": "Invalid Token"}), 401

# Start the Flask server
if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080, threaded=True) # Runs the server on machine's IP address
