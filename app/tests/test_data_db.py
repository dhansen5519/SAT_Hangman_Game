# Purpose: Test demo data has been correctly inserted by the data_db.py script
# Assumptions: You have already run the setup_db.py and data_db.py scripts
# Usage: Run python test_data_db.py from within the tests directory

import mysql.connector
from mysql.connector import errorcode

try:
    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()

    # Tests to validate words table has correct values
    c.execute("select * from words where word_id=1;")
    word = c.fetchall()[0][1]
    assert(word == "abase")

    c.execute("select * from words where word_id=936;")
    word = c.fetchall()[0][1]
    assert(word == "zephyr")

    # Tests to validate games table has correct values
    c.execute("select * from games where game_id=1;")
    user = c.fetchall()[0][1]
    assert(user == "Zero Cool")

    c.execute("select * from games where game_id=4;")
    user = c.fetchall()[0][1]
    assert(user == "The Phantom Phreak")

    # Tests to validate games_words table has correct values
    c.execute("select * from games_words where game_id=1;")
    word_id = c.fetchall()[0][1]
    assert(word_id == 10)

    c.execute("select * from games_words where game_id=4;")
    word_id = c.fetchall()[0][1]
    assert(word_id == 100)

    print("Tests completed")

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
