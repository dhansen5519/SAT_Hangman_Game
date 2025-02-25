# Purpose: Test content on statistics page is correct
# Usage: Run python -m pytest -v from within the app directory

import mysql.connector

def test_statistics(app, client):

    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()

    response = client.get('/statistics')
    assert response.status_code == 200

    # Validate number of games is correct
    c.execute("select count(*) from games;")
    count = c.fetchall()[0][0]
    assert "Number of games played: "+ str(count) in response.data.decode('utf-8')

    # Validate number of words is correct
    c.execute("select count(*) from words;")
    count = c.fetchall()[0][0]
    assert "Number of words available: "+ str(count) in response.data.decode('utf-8')

    # Validate average game score is correct
    c.execute("select avg(score) from games;")
    avg = c.fetchall()[0][0]
    assert "Average Game Score: "+ str('{0:,.2f}'.format(avg)) in response.data.decode('utf-8')

    # Validate highest game score is correct
    c.execute("select max(score) from games;")
    high = c.fetchall()[0][0]
    assert "Highest Score: "+ str(high) in response.data.decode('utf-8')

    # Validate lowest game score is correct
    c.execute("select min(score) from games;")
    low = c.fetchall()[0][0]
    assert "Lowest Score: "+ str(low) in response.data.decode('utf-8')

    # Validate most common word solved in a game
    c.execute("select word from words where word_id=(select word_id from games_words group by word_id order by count(word_id) desc limit 1);")
    common = c.fetchall()[0][0]
    assert "Most common word solved in a game: "+ str(common) in response.data.decode('utf-8')

    # Validate the user who has completed the most games
    c.execute("select user from games group by user order by count(user) desc limit 1;")
    user = c.fetchall()[0][0]
    assert "User who has played the most games: "+ str(user) in response.data.decode('utf-8')

    c.close()
    cnx.close()

    
