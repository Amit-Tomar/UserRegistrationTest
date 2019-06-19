* All APIs are documented using Postman : https://documenter.getpostman.com/view/3691246/S1Zz69Ub
* APIs are hosted on Digital Ocean Droplet : http://139.59.12.82:8080/

## Implementation Points

1. Passwords should be of length atleast 8, no other restrictions.
2. e-mail IDs in system are unique.
3. User name, email id and passwords can not be blank.
4. JWT based auth token, expires in 300 seconds.
5. DB used is SQLite hosted on Droplet itself.
6. To test, token should be passed as Bearer Token in Authorization header.
7. Passwords are stored in DB has salted hashes.

## HTTP Codes in response:

1. 500 : Internal error
2. 422 : Illformed inputs
3. 401 : Auth failed

## Pending :

1. No way of verifying if the user is actual owner of the email id he is registering with.
2. Invalidating token.