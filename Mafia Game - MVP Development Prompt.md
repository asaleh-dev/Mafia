## **Project: Mafia Web Game \- MVP Development with Python & Streamlit**

**1\. Game Overview:**

Develop a Minimum Viable Product (MVP) for a web-based social deduction game titled "Mafia". The game revolves around players receiving roles within a generated story where one player has been 'killed'. One player is secretly the 'Mafia' responsible. Players must deduce the Mafia's identity through discussion (offline) and voting (online), using clues revealed each round by the 'killed' player's persona.

**2\. Core MVP Features:**

* **Game Room Management:**  
  * Allow a user (admin) to create a game room.  
  * Generate a unique 6-character alphanumeric code for joining the room.  
  * Allow other players to join the room using the code.  
  * Display the list of joined players in the lobby.  
  * Admin control to start the game once the desired number of players have joined.  
* **Game Setup:**  
  * Input: Number of players (from the lobby).  
  * LLM Integration (OpenRouter \- Free Tier Models):  
    * Generate a unique, engaging story based on the player count.  
    * The story must establish a setting, introduce characters (one for each player), define relationships between characters, and narrate a murder.  
    * Randomly assign one player the role of 'Mafia'.  
    * Randomly assign one player the role of 'Killed'. (Ensure Mafia and Killed are different players).  
    * Generate 3-5 sequential clues related to the story that subtly point towards the Mafia.  
    * Include a plot twist within the story narrative.  
  * Information Distribution:  
    * Display the main story narrative to all players.  
    * Privately display each player's assigned character description and their role (Mafia or Civilian) to only that player. Indicate clearly who the 'killed' player is to everyone.  
* **Gameplay Loop:**  
  * **Investigation Phase:** Instruct players to discuss and investigate *offline* (outside the app).  
  * **Voting Phase:**  
    * Initiate an online voting round.  
    * Each active player votes for one other active player they suspect is the Mafia.  
    * Display voting results clearly (who voted for whom, and the final tally).  
  * **Revelation Phase:**  
    * Identify the player with the most votes. (Handle ties simply for MVP \- e.g., random choice among tied players, or no elimination if tied).  
    * Reveal if the voted player was the Mafia.  
  * **Outcome & Next Round:**  
    * **Mafia Caught:** If the voted player *was* the Mafia, the game ends, and Civilians win. Display a "Civilians Win\!" message.  
    * **Civilian Voted Out:** If the voted player was *not* the Mafia:  
      * Eliminate that player from the game (they can no longer vote).  
      * Check Win Condition: If only the Mafia and one Civilian remain, the Mafia wins. Display a "Mafia Wins\!" message.  
      * **Reveal Clue:** If the game continues, the 'killed' player's persona reveals the next clue from the generated list to all remaining players.  
      * Proceed to the next investigation/voting round.  
* **User Interface (Basic):**  
  * Lobby screen (create/join, player list, start button for admin).  
  * Game screen displaying:  
    * Main story text.  
    * Private character/role information.  
    * Current round number.  
    * Revealed clues.  
    * Voting interface (list of players to vote for).  
    * Voting results.  
    * Game status messages (e.g., "Waiting for votes", "Player X was eliminated", "Mafia Wins\!").

**3\. Key Technical Considerations:**

* **Platform:** Web Application built with Python and Streamlit.  
* **Backend & Frontend:** Streamlit for the entire application development:
  * Utilize Streamlit's session state for managing game data.
  * Leverage Streamlit components and widgets for UI elements.
  * Use Streamlit's built-in caching capabilities for performance optimization.
* **Real-time Communication:** Use Streamlit's experimental features or complementary solutions:
  * Implement periodic refreshing using Streamlit's rerun functionality.
  * Consider using Streamlit-Socketio for more responsive real-time functionality.
  * Explore Streamlit WebSocket components from the community.
* **State Management:** 
  * Use Streamlit session state for managing game rooms and player information.
  * Implement a server-side caching mechanism for game state persistence.
  * Consider supplementing with a lightweight database (SQLite) for more robust state management.
* **API Integration:** Use Python's requests library or OpenAI's Python SDK to interface with the OpenRouter API, sending prompts and processing the generated story, roles, and clues in JSON format.
* **Deployment:** Deploy on Streamlit Cloud or other Python-friendly hosting platforms (Heroku, PythonAnywhere, etc.).

**4\. LLM Story Generation Prompt Details (Example):**

* **Input to LLM:** Number of players (N).  
* **Required Output Format (JSON):**  
  {  
    "main\_story": "A detailed narrative setting the scene, introducing the murder mystery, and incorporating a plot twist.",  
    "killed\_character\_name": "Name of the character who was killed.",  
    "players": \[  
      {  
        "character\_name": "Character Name 1",  
        "character\_description": "Background, personality, relationship to the victim.",  
        "is\_mafia": false,  
        "is\_killed": false  
      },  
      {  
        "character\_name": "Character Name 2",  
        "character\_description": "...",  
        "is\_mafia": true, // Only one true  
        "is\_killed": false  
      },  
      {  
        "character\_name": "Character Name 3",  
        "character\_description": "...",  
        "is\_mafia": false,  
        "is\_killed": true // Only one true  
      }  
      // ... N player objects total  
    \],  
    "clues": \[  
      "First clue string.",  
      "Second clue string.",  
      "Third clue string."  
      // 3 to 5 clues total  
    \]  
  }

* **Instructions for LLM:** "Generate a Mafia game scenario for N players. Create unique characters with descriptions and relationships to the victim. Randomly assign one player as 'Mafia' and one as 'Killed'. Write an engaging main\_story including a plot twist. Provide 3-5 sequential clues that hint at the Mafia's identity without being too obvious. Ensure exactly one is\_mafia is true and exactly one is\_killed is true across all players. Output *only* the JSON object described above."

**5\. Python & Streamlit Implementation Details:**

* **Required Libraries:**
  * Streamlit (core framework)
  * Requests (API calls to OpenRouter)
  * Python-dotenv (environment variable management)
  * UUID (for generating unique room codes)
  * Optional: SQLite or other lightweight database
  * Optional: Streamlit-Socketio or similar for enhanced real-time features

* **Project Structure:**
  ```
  mafia_game/
  ├── app.py                # Main Streamlit application entry point
  ├── requirements.txt      # Python dependencies
  ├── .env                  # Environment variables (API keys, etc.)
  ├── utils/
  │   ├── openrouter.py     # OpenRouter API integration
  │   ├── game_state.py     # Game state management functions
  │   └── storyteller.py    # Story generation and processing
  ├── pages/
  │   ├── lobby.py          # Game lobby UI and logic
  │   ├── game.py           # Main game UI and logic
  │   └── results.py        # End game results
  └── README.md             # Project documentation
  ```

**6\. Exclusions for MVP:**

* In-app chat functionality.  
* Multiple Mafia members or complex roles (Doctor, Detective, etc.).  
* Persistent user accounts or game history.  
* Advanced UI/UX features (animations, detailed graphics).  
* Sophisticated tie-breaking logic in voting.  
* Mobile app versions.

**7\. MVP Goal:**

Deliver a functional Streamlit web application where a group of players can join a room, receive roles within an LLM-generated story, conduct voting rounds, receive clues, and reach a win/loss condition based on identifying the Mafia or eliminating all Civilians. The core loop must be playable and stable, utilizing Streamlit's capabilities for a clean and responsive user experience.