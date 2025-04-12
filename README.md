# Mafia Game

A web-based social deduction game built with Python and Streamlit where players take on roles within a generated story. One player is secretly the 'Mafia' responsible for a 'killing', and players must deduce their identity through discussion and voting.

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r mafia_game/requirements.txt
   ```
3. Make sure the OpenRouter API key is set in `mafia_game/.env`

### Running the Game

Navigate to the project root directory and run:
```
cd mafia_game
streamlit run app.py
```

This will start the Streamlit server and open the game in your default web browser.

## How to Play

1. **Create a Game**: One player creates a game room and gets a unique code
2. **Join a Game**: Other players join using the room code
3. **Start the Game**: The room admin starts the game
4. **Play the Game**:
   - Each player receives a character and role (Mafia, Civilian, or Killed)
   - Players discuss offline to identify the Mafia
   - Players vote in the app
   - The eliminated player is revealed
   - A new clue is revealed each round
   - Game continues until either the Mafia is caught or only the Mafia and one Civilian remain

## Project Structure

The game is built with Python and Streamlit, using OpenRouter's API to generate unique stories with the Google Gemini model.

- `mafia_game/app.py` - Main Streamlit application
- `mafia_game/utils/` - Helper functions and game logic
  - `openrouter.py` - API integration with OpenRouter
  - `game_state.py` - Game state management
  - `storyteller.py` - Story generation and processing

## Notes for Multiple Players

To play with multiple players:
1. Start the app on a machine accessible to all players on the network
2. Share the URL with other players
3. Each player accesses the game through their own device and browser 