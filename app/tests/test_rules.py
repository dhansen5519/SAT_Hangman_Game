# Purpose: Test to make sure that the rules pages loads correctly
# Usage: Run python -m pytest -v from within the app directory

def test_rules(client):
    response = client.get('/Rules')
    assert response.status_code == 200
    assert b"<h1>Rules of the Game</h1>" in response.data
