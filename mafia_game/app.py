import streamlit as st
import time
import json
from utils import game_state, openrouter, storyteller

# Import but don't use socket handler yet - it's available for external integration
from utils import socket_handler

st.set_page_config(
    page_title="Mafia Game",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if not already present
if "player_name" not in st.session_state:
    st.session_state.player_name = None
if "room_code" not in st.session_state:
    st.session_state.room_code = None
if "game_phase" not in st.session_state:
    st.session_state.game_phase = "welcome"  # welcome, create_room, join_room, lobby, game, results
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "player_count" not in st.session_state:
    st.session_state.player_count = 0
if "last_status_check" not in st.session_state:
    st.session_state.last_status_check = time.time()
if "last_update_timestamp" not in st.session_state:
    st.session_state.last_update_timestamp = 0
if "current_suspect" not in st.session_state:
    st.session_state.current_suspect = None
if "needs_refresh" not in st.session_state:
    st.session_state.needs_refresh = False
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# Register a callback for game state changes - this would be used for WebSocket integration
# This is optional and can be enabled when integrating with external platforms
# game_state.register_callback("streamlit_app", socket_handler.game_state_callback)

# Try to retrieve session data from URL parameters on page load/refresh
def restore_session_from_query_params():
    if "player_name" in st.query_params and "room_code" in st.query_params:
        player_name = st.query_params["player_name"]
        room_code = st.query_params["room_code"]
        
        # Check if room exists
        room_summary = game_state.get_room_summary(room_code)
        if room_summary and player_name in room_summary["players"]:
            st.session_state.player_name = player_name
            st.session_state.room_code = room_code
            
            # Set appropriate game phase based on room status
            if room_summary["status"] == "lobby":
                st.session_state.game_phase = "lobby"
            elif room_summary["status"] == "playing":
                st.session_state.game_phase = "game"
            elif room_summary["status"] == "ended":
                st.session_state.game_phase = "results"

# Update URL parameters to persist session data
def update_query_params():
    if st.session_state.player_name and st.session_state.room_code:
        st.query_params["player_name"] = st.session_state.player_name
        st.query_params["room_code"] = st.session_state.room_code
    else:
        # Clear all query parameters
        for key in list(st.query_params.keys()):
            del st.query_params[key]

# Refresh very frequently (every 0.5 seconds) to update game state
def auto_refresh():
    current_time = time.time()
    # Use a longer interval to reduce browser strain but still maintain responsiveness
    if current_time - st.session_state.last_refresh > 2.0:
        st.session_state.last_refresh = current_time
        check_for_updates()
        # Only rerun if there are actual changes detected
        if st.session_state.needs_refresh:
            st.session_state.needs_refresh = False
            st.rerun()

# Check for any updates in game state
def check_for_updates():
    # Initialize the refresh flag
    if "needs_refresh" not in st.session_state:
        st.session_state.needs_refresh = False
    
    # Check if we're in a game room
    if not st.session_state.room_code or not st.session_state.player_name:
        return
    
    # Get the latest room summary
    room_summary = game_state.get_room_summary(st.session_state.room_code)
    if not room_summary:
        return
    
    # Check for suspect selection changes
    if st.session_state.current_suspect != room_summary.get("current_suspect"):
        st.session_state.current_suspect = room_summary.get("current_suspect")
        st.session_state.needs_refresh = True
    
    # Check for player count changes
    current_player_count = len(room_summary["players"])
    if "player_count" in st.session_state and current_player_count != st.session_state.player_count:
        st.session_state.player_count = current_player_count
        st.session_state.needs_refresh = True
    
    # Check if there's a new update based on the timestamp
    if room_summary["last_update"] != st.session_state.last_update_timestamp:
        st.session_state.last_update_timestamp = room_summary["last_update"]
        st.session_state.needs_refresh = True
        
        # Phase transitions
        if st.session_state.game_phase == "lobby" and room_summary["status"] == "playing":
            st.session_state.game_phase = "game"
            st.session_state.needs_refresh = True
        elif st.session_state.game_phase == "game" and room_summary["status"] == "ended":
            st.session_state.game_phase = "results"
            st.session_state.needs_refresh = True
        elif st.session_state.game_phase == "game" and room_summary["status"] == "lobby":
            st.session_state.game_phase = "lobby"
            st.session_state.needs_refresh = True
        
        # Force rerun on any update to keep UI in sync
        st.rerun()

# Welcome page
def welcome_page():
    st.title("🕵️ Mafia Game")
    
    st.markdown("""
    Welcome to the Mafia Game, a social deduction game where players are assigned roles within a murder mystery.
    
    One player is secretly the "Killer," and players must work together to identify who it is.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Create Room", use_container_width=True):
            st.session_state.game_phase = "create_room"
            st.rerun()
    
    with col2:
        if st.button("Join Room", use_container_width=True):
            st.session_state.game_phase = "join_room"
            st.rerun()

# Create room page
def create_room_page():
    st.title("Create New Room")
    
    with st.form("create_room_form"):
        player_name = st.text_input("Your Name", max_chars=20)
        submit = st.form_submit_button("Create Room")
        
        if submit and player_name:
            st.session_state.player_name = player_name
            room_code, _ = game_state.create_game_room(player_name)
            st.session_state.room_code = room_code
            st.session_state.game_phase = "lobby"
            update_query_params()
            st.rerun()
    
    if st.button("Back"):
        st.session_state.game_phase = "welcome"
        st.rerun()

# Join room page
def join_room_page():
    st.title("Join Room")
    
    with st.form("join_room_form"):
        room_code = st.text_input("Room Code", max_chars=6).upper()
        player_name = st.text_input("Your Name", max_chars=20)
        submit = st.form_submit_button("Join")
        
        if submit and room_code and player_name:
            # Try to join the room
            joined = game_state.join_game_room(room_code, player_name)
            
            if joined:
                st.session_state.player_name = player_name
                st.session_state.room_code = room_code
                
                # Determine game phase from room status
                room_summary = game_state.get_room_summary(room_code)
                if room_summary["status"] == "lobby":
                    st.session_state.game_phase = "lobby"
                elif room_summary["status"] == "playing":
                    st.session_state.game_phase = "game"
                elif room_summary["status"] == "ended":
                    st.session_state.game_phase = "results"
                
                update_query_params()
                st.rerun()
            else:
                # Check if room exists but game has already started
                room_summary = game_state.get_room_summary(room_code)
                if room_summary and room_summary["status"] != "lobby":
                    st.error("The game has already started and cannot accept new players.")
                else:
                    st.error("Could not join the room. Check the room code and try again.")
    
    if st.button("Back"):
        st.session_state.game_phase = "welcome"
        st.rerun()

# Lobby page
def lobby_page():
    room_code = st.session_state.room_code
    player_name = st.session_state.player_name
    
    # Get room info
    room_summary = game_state.get_room_summary(room_code)
    player_info = game_state.get_player_info(room_code, player_name)
    
    if not room_summary or not player_info:
        st.error("Room not found or you are not a member. Returning to the home page.")
        st.session_state.player_name = None
        st.session_state.room_code = None
        st.session_state.game_phase = "welcome"
        update_query_params()
        st.rerun()
    
    # If game has started, redirect to game page
    if room_summary["status"] == "playing":
        st.session_state.game_phase = "game"
        st.rerun()
    elif room_summary["status"] == "ended":
        st.session_state.game_phase = "results"
        st.rerun()
    
    st.title("Waiting Room")
    
    # Display room code and player list
    st.markdown(f"### Room Code: **{room_code}**")
    st.markdown("Share this code with other players so they can join the game.")
    
    # Player list with a container to make refreshing more noticeable
    player_list_container = st.container()
    with player_list_container:
        st.markdown("### Players:")
        for idx, p in enumerate(room_summary["players"]):
            if p == room_summary["admin"]:
                st.markdown(f"{idx+1}. {p} (Admin)")
            else:
                st.markdown(f"{idx+1}. {p}")
    
    # Track player count changes to update session state
    current_player_count = len(room_summary["players"])
    if not hasattr(st.session_state, "player_count") or current_player_count != st.session_state.player_count:
        st.session_state.player_count = current_player_count
        # We no longer need to call st.rerun() here as the auto_refresh will handle it
    
    # Admin controls
    if player_info["is_admin"]:
        st.markdown("### Admin Controls")
        
        min_players = 3
        can_start = len(room_summary["players"]) >= min_players
        
        if not can_start:
            st.warning(f"At least {min_players} players are required to start the game.")
        
        start_col, settings_col = st.columns([1, 1])
        
        with start_col:
            if st.button("Start Game", disabled=not can_start):
                with st.spinner("Creating story..."):
                    try:
                        # Generate story
                        num_players = len(room_summary["players"])
                        story_data = storyteller.generate_game_story(num_players)
                        
                        # Start the game
                        success = game_state.start_game(room_code, story_data)
                        
                        if success:
                            st.session_state.game_phase = "game"
                            update_query_params()
                            st.rerun()
                        else:
                            st.error("Failed to start the game.")
                    except Exception as e:
                        st.error(f"Error starting game: {str(e)}")
    
    # Leave game button
    if st.button("Leave Game"):
        st.session_state.player_name = None
        st.session_state.room_code = None
        st.session_state.game_phase = "welcome"
        update_query_params()
        st.rerun()
    
    # Manual refresh button for player list
    if st.button("Refresh Player List"):
        # No need to do anything here - just clicking will trigger a refresh
        pass
    
    # Show current player count for visibility
    st.info(f"Currently {current_player_count} players in the room")
    
    # Auto-refresh to update player list
    auto_refresh()

# Game page
def game_page():
    room_code = st.session_state.room_code
    player_name = st.session_state.player_name
    
    # Get room and player info
    room_summary = game_state.get_room_summary(room_code)
    player_info = game_state.get_player_info(room_code, player_name)
    
    if not room_summary or not player_info:
        st.error("Room not found or you are not a member. Returning to the home page.")
        st.session_state.player_name = None
        st.session_state.room_code = None
        st.session_state.game_phase = "welcome"
        update_query_params()
        st.rerun()
    
    # Update tracking variables for state changes
    st.session_state.last_update_timestamp = room_summary.get("last_update", 0)
    st.session_state.current_suspect = room_summary.get("current_suspect")
    
    # If game is still in lobby, redirect to lobby
    if room_summary["status"] == "lobby":
        st.session_state.game_phase = "lobby"
        st.rerun()
    
    # If game has ended, go to results page
    if room_summary["status"] == "ended":
        st.session_state.game_phase = "results"
        st.rerun()
    
    # Main game layout
    st.title("Mafia Game")
    
    # Status indicator for real-time updates
    with st.container():
        col1, col2 = st.columns([9, 1])
        with col2:
            # Increment refresh counter to show updates are happening
            st.session_state.refresh_counter += 1
            # This element changes with each refresh but is visually hidden
            st.markdown(f'<div style="display:none">{st.session_state.refresh_counter}</div>', unsafe_allow_html=True)
            
            # Manual refresh button
            if st.button("🔄"):
                # This will trigger a rerun just by clicking
                pass
    
    # Role and info sidebar
    with st.sidebar:
        st.markdown("### Your Character")
        
        # Display character information
        killed_character_name = room_summary.get("killed_character_name", "Unknown")
        role_description = storyteller.format_role_description(
            {
                "character_name": player_info["character_name"],
                "character_description": player_info["character_description"],
                "is_mafia": player_info["is_mafia"]
            },
            killed_character_name
        )
        st.markdown(role_description)
        
        # Status indicator
        if player_info["is_eliminated"]:
            st.error("You have been eliminated from the game!")
        
        # Room info
        st.markdown(f"**Room Code:** {room_code}")
        st.markdown(f"**Round:** {room_summary['current_round']}")
        
        # Connection status
        st.markdown(f"**Last update:** {time.strftime('%H:%M:%S', time.localtime())}")
    
    # Main story container
    with st.container():
        # Story tab and discussion tab
        story_tab, discussion_tab = st.tabs(["Story & Clues", "Discussion"])
        
        with story_tab:
            # Display main story
            st.markdown(storyteller.format_main_story(room_summary))
            
            # Display revealed clues
            st.markdown("## Discovered Clues")
            
            clues = room_summary.get("revealed_clues", [])
            total_clues = len(clues)
            
            for i, clue in enumerate(clues):
                st.markdown(storyteller.format_clue(clue, i+1, total_clues))
            
            # Display current round instructions
            st.markdown(storyteller.format_round_instructions(room_summary["current_round"]))
        
        with discussion_tab:
            st.markdown("## Discussion and Accusation")
            
            # Get list of alive players
            alive_players = [p for p in room_summary["players"] if p not in room_summary["eliminated_players"]]
            
            # Show current suspect if one is selected
            if room_summary.get("current_suspect"):
                suspect = room_summary["current_suspect"]
                st.warning(f"Admin suspects: **{suspect}**")
            
            # Admin controls for suspect selection
            if player_info["is_admin"]:
                st.markdown("### Admin Controls")
                st.info("Players should discuss the case outside the app, then the admin selects a suspect based on the discussion.")
                
                # Select suspect
                suspect_options = [p for p in alive_players if p != player_name]
                if suspect_options:
                    selected_suspect = st.selectbox(
                        "Select suspect:",
                        suspect_options
                    )
                    
                    # Set suspect button
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Select Suspect"):
                            success = game_state.set_admin_suspect(room_code, selected_suspect)
                            if success:
                                st.session_state.current_suspect = selected_suspect
                                st.session_state.needs_refresh = True
                                st.rerun()
                    
                    # Accuse button (only show if suspect is selected)
                    with col2:
                        if room_summary.get("current_suspect"):
                            if st.button("Accuse Suspect", type="primary"):
                                result = game_state.process_admin_accusation(room_code)
                                if "error" not in result:
                                    st.session_state.needs_refresh = True
                                    st.rerun()
                                else:
                                    st.error(f"Error processing accusation: {result['error']}")
            else:
                # Non-admin players see status of accusation
                st.info("Wait for the admin to select a suspect based on your offline discussion.")
                
                if room_summary.get("current_suspect"):
                    st.warning(f"Admin suspects: **{room_summary['current_suspect']}**")
                    
                    # Check accusation result button
                    if st.button("Check Accusation Result"):
                        st.session_state.needs_refresh = True
                        st.rerun()  # Just refresh to see any changes
            
            # Display eliminated players
            if room_summary["eliminated_players"]:
                st.markdown("### Eliminated Players")
                for eliminated in room_summary["eliminated_players"]:
                    st.markdown(f"- {eliminated}")
    
    # Auto-refresh to update game state
    auto_refresh()

# Results page
def results_page():
    room_code = st.session_state.room_code
    player_name = st.session_state.player_name
    
    # Get room info
    room_summary = game_state.get_room_summary(room_code)
    
    if not room_summary:
        st.error("Room not found. Returning to the home page.")
        st.session_state.player_name = None
        st.session_state.room_code = None
        st.session_state.game_phase = "welcome"
        update_query_params()
        st.rerun()
    
    # If game is not ended, redirect to appropriate page
    if room_summary["status"] == "lobby":
        st.session_state.game_phase = "lobby"
        st.rerun()
    elif room_summary["status"] == "playing":
        st.session_state.game_phase = "game"
        st.rerun()
    
    # Get the winner
    winner = None
    suspected_player = None
    character_name = None
    
    if room_summary["game_result"] == "civilians_win":
        winner = "civilians"
        
        # Find the Mafia player
        for p_name in room_summary["players"]:
            p_info = game_state.get_player_info(room_code, p_name)
            if p_info and p_info.get("is_mafia"):
                suspected_player = p_name
                character_name = p_info["character_name"]
                break
    
    elif room_summary["game_result"] == "mafia_wins":
        winner = "mafia"
    
    # Display results
    st.title("Game Results")
    
    if winner:
        st.markdown(storyteller.format_game_results(winner, suspected_player, character_name))
    else:
        st.error("Could not determine game result.")
    
    # Admin controls
    player_info = game_state.get_player_info(room_code, player_name)
    
    if player_info and player_info["is_admin"]:
        st.markdown("### Admin Controls")
        
        if st.button("Play Again"):
            if game_state.reset_game(room_code):
                st.session_state.game_phase = "lobby"
                st.rerun()
            else:
                st.error("Failed to reset game.")
    
    if st.button("Return to Main Menu"):
        st.session_state.player_name = None
        st.session_state.room_code = None
        st.session_state.game_phase = "welcome"
        update_query_params()
        st.rerun()

# Main app control flow
def main():
    # Restore session from URL parameters if coming from a refresh
    restore_session_from_query_params()
    
    # Add custom CSS for styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add JavaScript for periodic refresh that's gentler on the browser
    st.markdown("""
    <script>
    // Set up periodic refresh without full page reload
    const intervalId = setInterval(function() {
        // This triggers a "heartbeat" to keep the session alive and check for updates
        const time = new Date().getTime();
        fetch(`/_stcore/stream?n=${time}`, { method: 'GET' });
    }, 3000); // Check every 3 seconds
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        clearInterval(intervalId);
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Display appropriate page based on game phase
    if st.session_state.game_phase == "welcome":
        welcome_page()
    elif st.session_state.game_phase == "create_room":
        create_room_page()
    elif st.session_state.game_phase == "join_room":
        join_room_page()
    elif st.session_state.game_phase == "lobby":
        lobby_page()
    elif st.session_state.game_phase == "game":
        game_page()
    elif st.session_state.game_phase == "results":
        results_page()

if __name__ == "__main__":
    main() 