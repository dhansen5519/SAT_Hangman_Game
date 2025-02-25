# Purpose: Test to ensure that the data from the leaderboard endpoint is displaying correctly on the page
# Assumption: you have already created the hangman database and run the setup_db.py and the data_db.py
# Usage: Run python -m pytest -v from within the app directory

from flask import json
from bs4 import BeautifulSoup
import mysql.connector

def test_leaderboard_data_matches_homepage(client):

    # Connect to mysql db
    cnx = mysql.connector.connect(user='root', password='projectpassword', host='127.0.0.1', database='hangman')
    c = cnx.cursor(dictionary=True)

    leaderboard_response = client.get('/')
    assert leaderboard_response.status_code == 200

    # Get the leaderboard data
    c.execute("SELECT user, MAX(score) AS high_score FROM games GROUP BY user ORDER BY high_score DESC LIMIT 10")
    leaderboard_data = c.fetchall()

    # Get the homepage HTML
    homepage_html = leaderboard_response.data.decode('utf-8')

    # Parse the homepage HTML
    soup = BeautifulSoup(homepage_html, 'html.parser')

    # Extract the leaderboard data from the homepage HTML
    homepage_leaderboard = []
    leaderboard_div = soup.find('div', class_='leaderboard')
    if leaderboard_div:
        for entry in leaderboard_div.find_all('div', class_='entry'):
            user = entry.find('span', class_='user').text.strip()
            score = entry.find('span', class_='score').text.strip()
            homepage_leaderboard.append({'user': user, 'high_score': float(score)})

    # Compare the data
    assert leaderboard_data == homepage_leaderboard, "Leaderboard data doesn't match homepage display"

    print("Leaderboard data from database:", leaderboard_data)
    print("Leaderboard data from homepage:", homepage_leaderboard)
