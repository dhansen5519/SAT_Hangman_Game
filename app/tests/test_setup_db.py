# Purpose: Test tables have been correctly setup using setup_db.py script
# Assumptions: You have already run the setup_db.py script
# Usage: Run python test_setup_db.py from within the tests directory

import mysql.connector
from mysql.connector import errorcode

try:
    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()

    # Validate games table has been created
    c.execute("select count(*) from information_schema.tables where table_schema='hangman' and table_name='games'");
    assert(c.fetchall()[0][0] == 1)

    # Validate words table has been created
    c.execute("select count(*) from information_schema.tables where table_schema='hangman' and table_name='words'");
    assert(c.fetchall()[0][0] == 1)

    # Validate games_words table has been created
    c.execute("select count(*) from information_schema.tables where table_schema='hangman' and table_name='games_words'");
    assert(c.fetchall()[0][0] == 1)

    # Validate columns in games table
    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='games' and column_name='game_id';")
    assert(c.fetchall()[0][0] == 'game_id')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='games' and column_name='user';")
    assert(c.fetchall()[0][0] == 'user')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='games' and column_name='score';")
    assert(c.fetchall()[0][0] == 'score')

    # Validate columns in words table
    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='words' and column_name='word_id';")
    assert(c.fetchall()[0][0] == 'word_id')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='words' and column_name='word';")
    assert(c.fetchall()[0][0] == 'word')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='words' and column_name='definition';")
    assert(c.fetchall()[0][0] == 'definition')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='words' and column_name='example_hint';")
    assert(c.fetchall()[0][0] == 'example_hint')

    # Validate columns in games_words table
    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='games_words' and column_name='game_id';")
    assert(c.fetchall()[0][0] == 'game_id')

    c.execute("select column_name from information_schema.columns where table_schema='hangman' and table_name='games_words' and column_name='word_id';")
    assert(c.fetchall()[0][0] == 'word_id')
    
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
