# Development Environment Setup

## Requirements

- Install python
- Clone project repository

Additional information located here: https://flask.palletsprojects.com/en/3.0.x/installation/ if get stuck.

### Python Version

Python version 3.11

## Setup .venv and install requirements

- First determine how you call python from the command line. Example "python", "python3", etc. I'm using "python" below.
- Make sure you are in the top directory where the requirements.txt file is located

Windows (in terminal in Visual Studio Code)

```
> python -m venv .venv
> cmd
> .venv\Scripts\activate
> pip install -r requirements.txt
```

Mac

```
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```

## Install MySQL and create database

* Install MySQL
* Create "hangman" database


## Setup tables in database and import data

Make sure hangman database is created and MySQL is running.

**Create tables and columns:**

From /app directory run

```
> python setup_db.py
```

If script completes without errors run the test script to validate tables were setup correctly.

From /app/tests/ run

```
> python test_setup_db.py
```

**Add data:**

From /app directory run

```
> python data_db.py
```

If script completes without errors run the test script to validate data was imported.

From /app/tests/ run

```
> python test_data_db.py
```

## Run Flask

Additional information located here: https://flask.palletsprojects.com/en/3.0.x/quickstart/

Windows/Mac

```
> flask run
```

The development website should now be running on http://127.0.0.1:5000

## Running pytest Tests

Add your test file to the tests/ directory with the naming convention of test_XXX.py.

To run all pytests
```
> python -m pytest -v
```
