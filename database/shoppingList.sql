CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT,
	user_name VARCHAR(64),
	email VARCHAR(64) UNIQUE,
	PRIMARY KEY (id)
);

CREATE TABLE family_users (
	family_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	PRIMARY KEY (family_id),
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE shopping_items (
	id INTEGER NOT NULL AUTO_INCREMENT,
	name VARCHAR(64),
    note VARCHAR(64),
    category VARCHAR(64),
    quantity INTEGER NOT NULL DEFAULT 0,
    family_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (family_id) REFERENCES family_users(family_id)
);

CREATE TABLE shopping_event (
	id INTEGER NOT NULL AUTO_INCREMENT,
	event_type VARCHAR(64),
    event_date VARCHAR(64),
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
	PRIMARY KEY (id)
);

-- Add new Users pairs
INSERT INTO users (user_name,email) VALUES ("Amit","amit@gmail.com")
INSERT INTO family_users VALUES (LAST_INSERT_ID(),LAST_INSERT_ID())

-- To get the cart for user with user_id as 1
SELECT * FROM users CROSS JOIN family_users CROSS JOIN shopping_items
WHERE shopping_items.family_id = family_users.family_id AND family_users.user_id = 1