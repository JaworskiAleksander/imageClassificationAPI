 | Resources | URLs | Method | Params | Status Code |
 | :--- | :--- | :---: | :--- | :--- |
 | Register | /register | POST | username<br>password | 200 ok<br>301 invalid username<br>302 invalid password |
 | Classify | /classify | POST | username<br>password<br>URL | 200 ok<br>301 invalid username<br>302 invalid password<br>303 out of tokens |
 | Refill | /refill | POST | username<br>admin_password<br>token_count | 200 ok<br>301 invalid username<br>304 invalid admin password |