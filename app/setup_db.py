# Purpose: Create tables and fields for SAT Hangman. May also be used to reset db tables.
# Assumptions: mysql is running locally and "hangman" database has already been created
# Usage: run python setup_db.py in the app directory

import mysql.connector
from mysql.connector import errorcode

try:
    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()
    print("Connected successfully to database")

    # Remove tables if exists
    c.execute("drop table if exists games_words;")
    c.execute("drop table if exists words;")
    c.execute("drop table if exists games;")

    # Create words table
    table_stmt = "CREATE TABLE words (word_id INT UNSIGNED NOT NULL AUTO_INCREMENT, word VARCHAR(100) NOT NULL, definition VARCHAR(255), example_hint varchar(255), PRIMARY KEY (word_id));"
    c.execute(table_stmt)
    print("words table was created")

    # Create games table
    table_stmt = "CREATE TABLE games (game_id INT UNSIGNED NOT NULL AUTO_INCREMENT, user VARCHAR(100), score DOUBLE, PRIMARY KEY (game_id));"
    c.execute(table_stmt)
    print("games table was created")

    # Create games_words table
    table_stmt = "CREATE TABLE games_words (game_id INT UNSIGNED NOT NULL, word_id INT UNSIGNED NOT NULL, PRIMARY KEY (game_id, word_id), FOREIGN KEY (game_id) REFERENCES games (game_id) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (word_id) REFERENCES words (word_id) ON DELETE CASCADE ON UPDATE CASCADE);"
    c.execute(table_stmt)
    print("games_words table was created")
    
    cnx.commit()
    c.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

else:
  cnx.close()
