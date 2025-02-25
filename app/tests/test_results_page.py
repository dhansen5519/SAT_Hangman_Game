# Purpose: Test content on results page is correct
# Usage: Run python -m pytest -v from within the app directory

import mysql.connector

def test_results_page(client):

    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor()

    response = client.get('/results')
    assert response.status_code == 200

    # Validate game id is correct
    c.execute("SELECT game_id FROM games ORDER BY game_id DESC LIMIT 1;")
    game_id = c.fetchone()[0]
    assert f"Game ID: {game_id}" in response.data.decode('utf-8')

    # Validate score is correct
    c.execute("SELECT score FROM games ORDER BY game_id DESC LIMIT 1;")
    score = c.fetchone()[0]
    assert f"Score: {score}" in response.data.decode('utf-8')

    # Validate words seen in the game
    c.execute("""
        SELECT w.word 
        FROM words w 
        JOIN games_words gw ON w.word_id = gw.word_id 
        WHERE gw.game_id = (SELECT game_id FROM games ORDER BY game_id DESC LIMIT 1);
    """)
    words = c.fetchall()
    for word in words:
        assert word[0] in response.data.decode('utf-8')

    c.close()
    cnx.close()
