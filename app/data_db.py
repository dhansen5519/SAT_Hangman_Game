# Purpose: Add demo data for SAT Hangman.
# Assumptions: mysql is running locally, "hangman" database has been created, and setup_db.py has been run
# Usage: run python data_db.py in the app directory

import mysql.connector
from mysql.connector import errorcode
import csv

try:
    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()
    print("Connected successfully to database")

    # Write CSV info to words table
    with open('../SAT_Words_Definitions.csv', 'r', encoding="utf8") as read_obj:
        csv_reader = csv.reader(read_obj)
        next(csv_reader, None)
        for row in csv_reader:
            c.execute("INSERT INTO words(word, definition, example_hint) VALUES (%s, %s, %s);",(row[0], row[2], row[4]))
        print("CSV data was inserted into words table")

    # Add data to games table
    table_stmt = "insert into games(user, score) values(%s, %s);"
    c.execute(table_stmt, ("Zero Cool", 55))
    c.execute(table_stmt, ("Crash Override", 25))
    c.execute(table_stmt, ("Cereal Killer", 31))
    c.execute(table_stmt, ("The Phantom Phreak", 10))
    print("data added to games table")

    # Add data to games_words table
    table_stmt = "insert into games_words(game_id, word_id) values(%s, %s);"
    c.execute(table_stmt, (1, 55))
    c.execute(table_stmt, (1, 25))
    c.execute(table_stmt, (1, 31))
    c.execute(table_stmt, (1, 10))

    c.execute(table_stmt, (2, 5))
    c.execute(table_stmt, (2, 2))
    c.execute(table_stmt, (2, 1))
    c.execute(table_stmt, (2, 11))

    c.execute(table_stmt, (3, 100))
    c.execute(table_stmt, (3, 250))
    c.execute(table_stmt, (3, 310))
    c.execute(table_stmt, (3, 105))

    c.execute(table_stmt, (4, 550))
    c.execute(table_stmt, (4, 250))
    c.execute(table_stmt, (4, 310))
    c.execute(table_stmt, (4, 100))
    print("data added to games_words table")
    
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
