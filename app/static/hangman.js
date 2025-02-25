let currentGameId = null;  // Define currentGameId globally
let attemptsLeft= 6;
let guessedLetters = []; 
let extra_lives=0; 
let currentWord = null;
let username = null;
document.addEventListener('DOMContentLoaded', () => {
document.addEventListener('DOMContentLoaded', function () {
    initializeGame();
});


const hangmanStages = [
    `
     +---+
     |   |
         |
         |
         |
         |
    =========`,
    `
     +---+
     |   |
     O   |
         |
         |
         |
    =========`,
    `
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========`,
    `
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========`,
    `
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========`,
    `
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========`,
    `
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========`
];

function updateHangmanAscii(wrongGuessesCount) {
    const hangmanAscii = document.getElementById('hangman-ascii');
    hangmanAscii.innerText = hangmanStages[wrongGuessesCount];
}

function setGameId(currentGameId) {
    document.getElementById('game-id').textContent = currentGameId;
    const form = document.querySelector(`form[action="{{ url_for('results') }}"]`);
    if (form) {
        const input = form.querySelector('input[name="game_id"]');
        if (input) {
            input.value = currentGameId;
        }
    }
}

updateHangmanAscii(0);
function initializeGame() {
    // Set up event listeners only after starting a new game successfully
    const usernameField = document.getElementById('username');
    const errorMessage = document.getElementById('error-message');

    // Clear previous error message
    errorMessage.textContent = '';

    if (usernameField.value.trim() === '') {
        errorMessage.textContent = 'Username is required.';
        return;
    }

    startNewGame().then(() => {
        // Set up event listeners for letter buttons
        document.querySelectorAll('.letter-button').forEach(button => {
            button.addEventListener('click', function () {
                const letter = this.dataset.letter;
                makeGuess(letter, this);
            });
        });

        // Set up event listeners for other buttons
        document.getElementById('get-hint').addEventListener('click', function () {
            fetch('/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('hint').innerText = `Hint: ${data.hint}`;
                document.getElementById('score').innerText = data.score;
            });
        });

        document.getElementById('skip-word').addEventListener('click', function () {
            fetch('/skip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(() => {
                updateStatus();
            });
        });

        document.getElementById('extra-life').addEventListener('click', function () {
            fetch('/extra_life', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('attempts').innerText = data.attempts;
                document.getElementById('score').innerText = data.score;
            });
        });

        // Load the initial word
        loadWord();
    }).catch(error => {
        console.error('Error initializing game:', error);
    });
}


function startNewGame() {
    const usernameField = document.getElementById('username');
    const errorMessage = document.getElementById('error-message');
    const gameSection = document.getElementById('game-info')
    const startGame = document.getElementById('start-game-button')
    // Clear previous error message
    errorMessage.textContent = '';

    if (usernameField.value.trim() === '') {
        errorMessage.textContent = 'Username is required.';
        return;
    }

    const username = usernameField.value.trim().toUpperCase();
    usernameField.value = username;
    usernameField.disabled = true;
    usernameField.style.backgroundColor = 'yellow'; // Light blue background
    usernameField.style.fontWeight = 'bold';         // Bold text
    gameSection.style.visibility = 'visible';
    startGame.style.visibility = 'hidden';

    return fetch('/start_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })  // Ensure you are sending a username
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`Network response was not ok: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.game_id) {
            console.log(`New game started with ID: ${data.game_id}`);
            currentGameId = data.game_id;
            setGameId(currentGameId);
        } else {
            console.error('Failed to start a new game');
        }
    })
    .catch(error => {
        console.error('Error starting a new game:', error);
    });
}



function makeGuess(letter, button) {
    if (currentGameId === null) {
        console.error('Current game ID is not defined.');
        return;
    }
    fetch('/guess', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_id: currentGameId,
            guess: letter,
            current_word: currentWord,
            guessed_letters: guessedLetters,
            wrong_guesses: wrongGuesses
        })
    })
    .then(response => response.json())
    .then(data => {
        // Handle response data
        console.log('Guess made:', data);

        if (data.error) {
            console.error('Error making guess:', data.error);
            return;
        }

        // Update UI with new game state
        guessedLetters = data.guessed_letters || guessedLetters;
        wrongGuesses = data.wrong_guesses || wrongGuesses;

        const currentScore = document.getElementById('score').innerText;

        if (data.correct) {
            document.getElementById('score').innerText = parseInt(currentScore) + 10
        } else {
            document.getElementById('score').innerText = parseInt(currentScore) - 5 
        }

        updateWordDisplay();
        updateGuessedLetters(letter);
        updateWrongGuesses();
        updateAttempts(data.correct - 1);
        updateHangmanAscii(wrongGuesses.length);

        button.disabled = true;
        button.classList.add(data.correct ? 'correct' : 'incorrect');

        // Handle game status updates
        if (data.status === 'won' || data.status === 'lost') {
            handleGameOver(data.status);
        }
    })
    .catch(error => {
        console.error('Error making guess:', error);
    });
}

function updateAttemptsDisplay() {
    document.getElementById('attempts').innerText = `Attempts remaining: ${attemptsLeft}`;
}

function updateAttempts(updatevalue) {
    const attemptsElement = document.getElementById('attempts');
    // Replace `currentAttemptsLeft` with the variable that holds the number of attempts left
    attemptsLeft=attemptsLeft+updatevalue; 
    attemptsElement.innerText = attemptsLeft; 
}

function updateWrongGuesses() {
    const wrongGuessesElement = document.getElementById('wrong-guesses');
    wrongGuessesElement.innerText = wrongGuesses.join(', ');
}

function updateGuessedLetters(letter) {
    guessedLetters.push(letter)
}

function handleGameOver(status) {
    const gameSection = document.getElementById('game-info');
    const startGameSection = document.getElementById('start-game-section');
    const getResults = document.getElementById('get-results');
    const score = document.getElementById('score').innerText;

    // Hide the game info section and show the start game section
    gameSection.style.display = 'none';
    startGameSection.style.display = 'block';
    getResults.style.display = 'block';

    // Update the score in the DB
    fetch(`/update_score?game_id=${encodeURIComponent(currentGameId)}&score=${encodeURIComponent(score)}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
    })
    .catch(error => {
        console.error('Error adding score to the database:', error);
    });


    if (status === 'won') {
        alert('Congratulations! You won!');
    } else if (status === 'lost') {
        alert('Game over! You lost!');
    }
}



function updateStatus() {
    if (currentGameId === null) {
        console.error('Current game ID is not defined.');
        return;
    }

    fetch('/status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ game_id: currentGameId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('score').innerText = data.score;
        document.getElementById('attempts').innerText = data.attempts;
        document.getElementById('wrong-guesses').innerText = data.wrong_guesses.join(', ');
        document.getElementById('guessed').innerText = data.guessed.join(' ');
        
        // Update the word display
        updateWordDisplay();
        
        if (data.hint) {
            document.getElementById('hint').innerText = `Hint: ${data.hint}`;
        }
    });
}

function getCurrentWord() {
    return currentWord;
}

function updateWordDisplay() {
    const wordDisplay = document.getElementById('word-display');
    const word = getCurrentWord();
    const displayText = word.split('').map(letter => {
        return guessedLetters.includes(letter) ? letter : '_';
    }).join(' ');
    wordDisplay.innerText = displayText;
}

function loadWord() {
    if (currentGameId === null) {
        console.error('Current game ID is not defined.');
        return;
    }

    fetch(`/get_word?game_id=${encodeURIComponent(currentGameId)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.word) {
                console.log(`The word is: ${data.word}`);

                // Set the current game ID and word
                currentWord = data.word;

                // Initialize guessed letters and wrong guesses
                guessedLetters = [];
                wrongGuesses = [];
                attemptsLeft = 6; // Set this to your initial value

                // Update UI
                updateWordDisplay();
                updateGuessedLetters();
                updateWrongGuesses();
                updateAttempts(0);
            } else {
                console.error('Failed to get a word');
            }
        })
        .catch(error => {
            console.error('Error fetching the word:', error);
        });
}



document.getElementById('start-game-button').addEventListener('click', function() {
    initializeGame().then(() => {
        // Proceed with game setup after successful game start
        document.querySelectorAll('.letter-button').forEach(button => {
            button.addEventListener('click', function () {
                const letter = this.dataset.letter;
                makeGuess(letter, this);
            });
        });

        document.getElementById('get-hint').addEventListener('click', function () {
            fetch('/hint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('hint').innerText = `Hint: ${data.hint}`;
                document.getElementById('score').innerText = data.score;
            });
        });

        document.getElementById('skip-word').addEventListener('click', function () {
            fetch('/skip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ game_id: currentGameId })
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Network response was not ok: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(`Server error: ${data.error}`);
                }
                updateStatus();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
        

        document.getElementById('extra-life').addEventListener('click', function () {
            fetch('/extra_life', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('attempts').innerText = data.attempts;
                document.getElementById('score').innerText = data.score;
            });
        });
    });
});
});
