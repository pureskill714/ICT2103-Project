## Blood Donation Management System

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