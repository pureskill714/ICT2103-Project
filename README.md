## Blood Donation Management System

### Populate MariaDB
A SQL script is provided in `database/generate_database.sql`.
The script will create and populate tables in MariaDB with data needed to use the application.

**Built-in accounts**

Role: Blood Bank Staff
- user1 (branch 10001)
- user2 (branch 10002)
- user3 (branch 10003)
- user4 (branch 10004)

Role: Healthcare Staff
- healthcare1

Password for all accounts
- 1234

### Running the project

Dependencies to install:
  * Python3
  * MariaDB

Install python dependencies with `pip install -r requirements.txt`.

MariaDB login credentials are read from environment variables.
Set them before running:

- mariadb username: `BLOODMGT_MARIADB_USER` 
- mariadb password: `BLOODMGT_MARIADB_PASS`

If you do not set them, you will be prompted to enter it when starting the application.

Finally, run with:
`python main.py`

### Database Selection

The application supports both **MariaDB** (Relational DB) and **Cloud Firestore** (NoSQL).

To switch between them, see line 26-27 in `main.py`:

```
# Use MariaDB
db = MariaDBBackend()
#db = FirebaseBackend()
```

```
# Use Firestore
#db = MariaDBBackend()
db = FirebaseBackend()
```

*Uncomment the desired database to use it.*

Note that the application expects MariaDB server running locally, be sure to start MariaDB server for it to work.
There is no need to setup anything for Firestore since it is cloud hosted.