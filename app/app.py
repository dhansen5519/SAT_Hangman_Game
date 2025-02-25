from flask import Flask, render_template, jsonify
import requests
import mysql.connector
from mysql.connector import errorcode
import random
from flask import request, url_for


app = Flask(__name__)

# Settings for MySQL
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'projectpassword'
app.config['MYSQL_DB'] = 'hangman'
app.config['MYSQL_PORT'] = 3306


# If you want to use `mysql.connector` for connections
db_config = {
    'user': app.config['MYSQL_USER'],
    'password': app.config['MYSQL_PASSWORD'],
    'host': app.config['MYSQL_HOST'],
    'database': app.config['MYSQL_DB'],
    'port': app.config['MYSQL_PORT']
}


@app.route("/")
def index():
    leaderboard_data = {'leaderboard': []}
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user, MAX(score) AS high_score FROM games GROUP BY user ORDER BY high_score DESC LIMIT 10")
        leaderboard_data = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({'error': 'Error retrieving leaderboard data'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template("HomePage.html", leaderboard=leaderboard_data)

@app.route("/play", methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        guess = request.form.get('guess')
        # Logic to handle guess
        return jsonify({'status': 'ongoing'})  # Adjust based on your logic
    # Render the game template
    return render_template('game.html')

@app.route("/results")
def results():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT game_id, score FROM games ORDER BY game_id DESC LIMIT 1")
    game = cursor.fetchone()
    if game:
        game_id = game['game_id']
        score = game['score']
        cursor.execute("SELECT w.word FROM words w JOIN games_words gw ON w.word_id = gw.word_id WHERE gw.game_id = %s", (game_id,))
        words = cursor.fetchall()
        words_count = len(words)
    else:
        game_id = None
        score = None
        words = []
        words_count = 0
    cursor.close()
    conn.close()
    return render_template('results.html', game_id=game_id, score=score, words=words, words_count=words_count)

   
# route for the Rules page
@app.route("/Rules")
def rules():
    return render_template("Rules.html")

@app.route("/statistics")
def stats():
# Hold data
  stat_data = {}

  try:
    # Connect to db
    conn = mysql.connector.connect(**db_config)
    c = conn.cursor()

    # Get number of games
    c.execute("select count(*) from games;")
    stat_data['game_count'] = c.fetchall()[0][0]

    # Get number of words
    c.execute("select count(*) from words;")
    stat_data['word_count'] = c.fetchall()[0][0]

    # Get average score
    c.execute("select avg(score) from games;")
    stat_data['avg_score'] = '{0:,.2f}'.format(c.fetchall()[0][0])

    # Get max score of all games
    c.execute("select max(score) from games;")
    stat_data['max_score'] = c.fetchall()[0][0]

    # Get min score of all games
    c.execute("select min(score) from games;")
    stat_data['min_score'] = c.fetchall()[0][0]

    # Get the most common word completed in a game
    c.execute("select word from words where word_id=(select word_id from games_words group by word_id order by count(word_id) desc limit 1);")
    stat_data['word_common'] = c.fetchall()[0][0]

    # Get the user who has completed the most games
    c.execute("select user from games group by user order by count(user) desc limit 1;")
    stat_data['most_games'] = c.fetchall()[0][0]

    c.close()
    conn.close()
    
  except Exception as e:
     return("<p>Sorry, there was an error loading the statistics</p>")
     
  return render_template("statistics.html", stats=stat_data)

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO games (user, score) VALUES (%s, %s)", (username, 0))
        game_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

    cursor.close()
    conn.close()

    return jsonify({'game_id': game_id}), 200

@app.route('/guess', methods=['POST'])
def guess():
    data = request.get_json()
    letter = data.get('guess')
    game_id = data.get('game_id')
    current_word = data.get('current_word')
    guessed_letters = data.get('guessed_letters', [])
    wrong_guesses = data.get('wrong_guesses', [])

    if not isinstance(guessed_letters, list) or not isinstance(wrong_guesses, list):
        return jsonify({'error': 'Invalid data format'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT word
        FROM words WHERE word = %s
    """, (current_word,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Game not found'}), 404

    word = result['word']

    if letter in guessed_letters or letter in wrong_guesses:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Letter already guessed'}), 400

    correct = letter in word

    if correct:
        if letter not in guessed_letters:
            guessed_letters.append(letter)
        if all_letters_guessed(word, guessed_letters):
            status = 'won'
        else:
            status = 'ongoing'
    else:
        wrong_guesses.append(letter)
        status = 'lost' if len(wrong_guesses) >= 6 else 'ongoing'

    return jsonify({
        'status': status,
        'correct': correct,
        'guessed_letters': guessed_letters,
        'wrong_guesses': wrong_guesses,
    })

def all_letters_guessed(word, guessed_letters):
    return all(letter in guessed_letters for letter in word if letter != ' ')

@app.route('/hint', methods=['POST'])
def hint():
    game_id = request.json.get('game_id')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT example_hint FROM games_words JOIN words ON games_words.word_id = words.word_id WHERE game_id = %s", (game_id,))
    hint = cursor.fetchone()['example_hint']
    cursor.close()
    conn.close()
    return jsonify({
        'hint': hint,
        'score': 10  # Example score update
    })

@app.route('/skip', methods=['POST'])
def skip():
    game_id = request.json.get('game_id')
    if not game_id:
        return jsonify({'error': 'Game ID is required.'}), 400
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT word_id 
            FROM games_words 
            WHERE game_id = %s
        """, (game_id,))
        used_words = {row['word_id'] for row in cursor.fetchall()}
        
        if not used_words:
            return jsonify({'error': 'No words found for the current game.'}), 404

        cursor.execute("""
            SELECT word_id, word 
            FROM words 
            WHERE word_id NOT IN (%s)
            ORDER BY RAND()
            LIMIT 1
        """, (', '.join(map(str, used_words)),))
        new_word = cursor.fetchone()

        if not new_word:
            return jsonify({'error': 'No more words available.'}), 404

        cursor.execute("""
            UPDATE games_words 
            SET word_id = %s 
            WHERE game_id = %s 
            LIMIT 1
        """, (new_word['word_id'], game_id))
        conn.commit()

        return jsonify({'word': new_word['word']})

    except mysql.connector.Error as err:
        return jsonify({'error': 'Database error occurred.'}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/extra_life', methods=['POST'])
def extra_life():
    game_id = request.json.get('game_id')
    return jsonify({
        'attempts': 3,  # Example attempt update
        'score': 20  # Example score update
    })

@app.route('/get_word', methods=['GET'])
def get_word():
    game_id = request.args.get('game_id')
    if not game_id:
        return jsonify({'error': 'Game ID is required'}), 400   

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM words")
        words = cursor.fetchall()

        if not words:
            return jsonify({'error': 'No words found in the database'}), 404

        word = random.choice(words)

        try:
            cursor.execute("INSERT INTO games_words (game_id, word_id) VALUES (%s, %s)", (game_id, word['word_id']))
        except: 
            return jsonify({'error': "games_words errors"}), 413

        conn.commit()
        cursor.close()
        
        return jsonify({'word': word['word']})
    
    except mysql.connector.Error as err:
        error_message = 'Database error'
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            error_message = 'Database does not exist'
        elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            error_message = 'Invalid username or password'
        return jsonify({'error': error_message}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/start_new_game', methods=['POST'])
def start_new_game():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("INSERT INTO games (user, score) VALUES (%s, %s)", (None, 0))
        game_id = cursor.lastrowid
        conn.commit()

        cursor.execute("""
            SELECT word_id, word 
            FROM words 
            ORDER BY RAND() 
            LIMIT 1
        """)
        word = cursor.fetchone()
        cursor.execute("INSERT INTO games_words (game_id, word_id) VALUES (%s, %s)", (game_id, word['word_id']))
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({'game_id': game_id, 'word': word['word']}), 200

@app.route('/update_score', methods=['GET'])
def update_score():
    # get game id and final score
    id = request.args.get('game_id')
    final = float(request.args.get('score'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # add score to the db
        cursor.execute("update games set score=%s where game_id=%s;", (final, id))
        conn.commit()
        return "ok", 200
    
    except mysql.connector.Error as err:
        error_message = 'Database error'
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            error_message = 'Database does not exist'
        elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            error_message = 'Invalid username or password'
        return jsonify({'error': error_message}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)
