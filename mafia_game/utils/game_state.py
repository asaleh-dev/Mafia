import uuid
import random
import time
from collections import defaultdict

# Game state dictionary to store all active game rooms
game_rooms = {}

class GameState:
    def __init__(self):
        # Initialize empty game state
        self.game_rooms = {}
        self.callbacks = {}  # Callback registry for external integrations
    
    def register_callback(self, callback_id, callback_fn):
        """
        Register a callback function that will be called when game state changes.
        Useful for external integrations like websockets or other real-time notification systems.
        
        Args:
            callback_id (str): Unique ID for the callback
            callback_fn (function): Function to call with (room_code, event_type) parameters
        """
        self.callbacks[callback_id] = callback_fn
    
    def unregister_callback(self, callback_id):
        """
        Unregister a previously registered callback.
        
        Args:
            callback_id (str): ID of the callback to remove
        """
        if callback_id in self.callbacks:
            del self.callbacks[callback_id]
    
    def _notify_callbacks(self, room_code, event_type):
        """
        Notify all registered callbacks about a game state change.
        
        Args:
            room_code (str): The room code where the event occurred
            event_type (str): Type of event (e.g., 'join', 'leave', 'suspect', 'accuse', etc.)
        """
        for callback_fn in self.callbacks.values():
            try:
                callback_fn(room_code, event_type)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def get_all_room_codes(self):
        """
        Get list of all active room codes.
        
        Returns:
            list: All active room codes
        """
        return list(self.game_rooms.keys())
    
    def generate_room_code(self):
        """
        Generate a unique 6-character alphanumeric room code.
        
        Returns:
            str: A unique room code
        """
        # Generate a random 6-character code
        code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
        
        # Ensure the code is unique
        while code in self.game_rooms:
            code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
        
        return code
    
    def create_game_room(self, admin_name):
        """
        Create a new game room with the given admin.
        
        Args:
            admin_name (str): The name of the admin player
            
        Returns:
            tuple: (room_code, room_data)
        """
        room_code = self.generate_room_code()
        
        room_data = {
            "admin": admin_name,
            "players": [admin_name],
            "status": "lobby",  # lobby, setup, playing, ended
            "story_data": None,
            "player_assignments": {},  # Maps player names to character indices
            "current_round": 0,
            "revealed_clues": [],
            "current_suspect": None,  # Player currently suspected by admin
            "eliminated_players": [],
            "game_result": None,  # "civilians_win", "mafia_wins", or None if game is ongoing
            "last_update": time.time()  # Timestamp of last update for synchronization
        }
        
        self.game_rooms[room_code] = room_data
        self._notify_callbacks(room_code, "create")
        return room_code, room_data
    
    def join_game_room(self, room_code, player_name):
        """
        Add a player to an existing game room.
        
        Args:
            room_code (str): The room code to join
            player_name (str): The name of the joining player
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room_code not in self.game_rooms:
            return False
        
        room = self.game_rooms[room_code]
        
        # Check if player already exists in the room
        if player_name in room["players"]:
            return True  # Allow rejoining if already in the room
        
        # Only allow new players to join in lobby phase
        if room["status"] != "lobby":
            return False
        
        room["players"].append(player_name)
        room["last_update"] = time.time()  # Use timestamp instead of UUID for better compatibility
        self._notify_callbacks(room_code, "join")
        return True
    
    def start_game(self, room_code, story_data):
        """
        Start a game with the given story data.
        
        Args:
            room_code (str): The room code
            story_data (dict): The story data from the LLM
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room_code not in self.game_rooms:
            return False
        
        room = self.game_rooms[room_code]
        
        if room["status"] != "lobby":
            return False
        
        if len(room["players"]) < 3:  # Minimum 3 players required
            return False
        
        # Assign characters to players (only Mafia or Civilian)
        players = room["players"].copy()
        random.shuffle(players)
        
        # Create player assignments
        player_assignments = {}
        for i, player in enumerate(players):
            player_assignments[player] = i % len(story_data["players"])
        
        # Randomly select one player to be Mafia
        mafia_player = random.choice(list(player_assignments.keys()))
        
        # Update player roles in story data
        for i in range(len(story_data["players"])):
            story_data["players"][i]["is_mafia"] = False
            story_data["players"][i]["is_killed"] = False  # No killed player role
        
        # Find which character index to make Mafia
        mafia_character_idx = player_assignments[mafia_player]
        story_data["players"][mafia_character_idx]["is_mafia"] = True
        
        room["status"] = "playing"
        room["story_data"] = story_data
        room["player_assignments"] = player_assignments
        room["current_round"] = 1
        room["revealed_clues"] = [story_data["clues"][0]]  # Reveal first clue
        room["current_suspect"] = None
        room["last_update"] = time.time()
        
        self._notify_callbacks(room_code, "start")
        return True
    
    def set_admin_suspect(self, room_code, suspect_name):
        """
        Set the admin's current suspect.
        
        Args:
            room_code (str): The room code
            suspect_name (str): The name of the suspected player
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room_code not in self.game_rooms:
            return False
        
        room = self.game_rooms[room_code]
        
        if room["status"] != "playing":
            return False
        
        if suspect_name not in room["players"]:
            return False
        
        room["current_suspect"] = suspect_name
        room["last_update"] = time.time()
        
        self._notify_callbacks(room_code, "suspect")
        return True
    
    def process_admin_accusation(self, room_code):
        """
        Process the admin's accusation against the current suspect.
        
        Args:
            room_code (str): The room code
            
        Returns:
            dict: Results of the accusation
        """
        room = self.game_rooms.get(room_code)
        if not room or room["status"] != "playing":
            return {"error": "Invalid game state"}
        
        suspect = room["current_suspect"]
        if not suspect:
            return {"error": "No suspect selected"}
        
        # Get character info for suspected player
        player_idx = room["player_assignments"][suspect]
        character_info = room["story_data"]["players"][player_idx]
        is_mafia = character_info["is_mafia"]
        
        result = {
            "suspected_player": suspect,
            "character_name": character_info["character_name"],
            "is_mafia": is_mafia
        }
        
        # Check if accusation was correct (suspect is Mafia)
        if is_mafia:
            room["status"] = "ended"
            room["game_result"] = "civilians_win"
            result["game_over"] = True
            result["winner"] = "civilians"
            self._notify_callbacks(room_code, "game_over")
        else:
            # Eliminate the wrongly accused player
            room["eliminated_players"].append(suspect)
            
            # Count remaining players
            active_players = [p for p in room["players"] if p not in room["eliminated_players"]]
            
            # Get number of mafia players remaining
            mafia_count = 0
            civilian_count = 0
            for player in active_players:
                player_idx = room["player_assignments"][player]
                if room["story_data"]["players"][player_idx]["is_mafia"]:
                    mafia_count += 1
                else:
                    civilian_count += 1
            
            # Check if Mafia wins (only 1 civilian left)
            if mafia_count == 1 and civilian_count == 1:
                room["status"] = "ended"
                room["game_result"] = "mafia_wins"
                result["game_over"] = True
                result["winner"] = "mafia"
                self._notify_callbacks(room_code, "game_over")
            else:
                # Continue to next round
                room["current_round"] += 1
                
                # Reveal next clue if available
                if room["current_round"] <= len(room["story_data"]["clues"]):
                    next_clue = room["story_data"]["clues"][room["current_round"] - 1]
                    room["revealed_clues"].append(next_clue)
                
                # Reset current suspect
                room["current_suspect"] = None
                
                result["game_over"] = False
                result["next_round"] = room["current_round"]
                
                if len(room["revealed_clues"]) >= len(room["story_data"]["clues"]):
                    result["new_clue"] = None
                else:
                    result["new_clue"] = room["revealed_clues"][-1]
                
                self._notify_callbacks(room_code, "next_round")
        
        room["last_update"] = time.time()
        return result
    
    def get_player_info(self, room_code, player_name):
        """
        Get information specific to a player.
        
        Args:
            room_code (str): The room code
            player_name (str): The player's name
            
        Returns:
            dict: Player-specific information or None if player not found
        """
        if room_code not in self.game_rooms:
            return None
        
        room = self.game_rooms[room_code]
        
        if player_name not in room["players"]:
            return None
        
        player_info = {
            "name": player_name,
            "is_admin": player_name == room["admin"],
            "is_eliminated": player_name in room["eliminated_players"]
        }
        
        # If game is playing or ended, add role information
        if room["status"] in ["playing", "ended"] and room["story_data"]:
            character_idx = room["player_assignments"].get(player_name, 0)
            character_info = room["story_data"]["players"][character_idx]
            
            player_info["character_name"] = character_info["character_name"]
            player_info["character_description"] = character_info["character_description"]
            player_info["is_mafia"] = character_info["is_mafia"]
        
        return player_info
    
    def get_room_summary(self, room_code):
        """
        Get a summary of the room state suitable for sharing with clients.
        
        Args:
            room_code (str): The room code
            
        Returns:
            dict: Room summary or None if room not found
        """
        if room_code not in self.game_rooms:
            return None
        
        room = self.game_rooms[room_code]
        
        # Create a sanitized copy with only the information all players should see
        summary = {
            "status": room["status"],
            "players": room["players"].copy(),
            "admin": room["admin"],
            "current_round": room["current_round"],
            "eliminated_players": room["eliminated_players"].copy(),
            "last_update": room["last_update"],
            "current_suspect": room["current_suspect"]
        }
        
        # Add game-specific information if game is in progress
        if room["status"] in ["playing", "ended"] and room["story_data"]:
            summary["main_story"] = room["story_data"]["main_story"]
            summary["killed_character_name"] = room["story_data"]["killed_character_name"]
            summary["revealed_clues"] = room["revealed_clues"].copy()
        
        # Add game result if game is ended
        if room["status"] == "ended":
            summary["game_result"] = room["game_result"]
        
        return summary
    
    def reset_game(self, room_code):
        """
        Reset a game room to lobby state but keep players.
        
        Args:
            room_code (str): The room code
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room_code not in self.game_rooms:
            return False
        
        room = self.game_rooms[room_code]
        
        # Only allow resetting if game has ended
        if room["status"] != "ended":
            return False
        
        # Keep players but reset game state
        players = room["players"].copy()
        admin = room["admin"]
        
        # Create a fresh room with same players
        room.clear()
        room.update({
            "admin": admin,
            "players": players,
            "status": "lobby",
            "story_data": None,
            "player_assignments": {},
            "current_round": 0,
            "revealed_clues": [],
            "current_suspect": None,
            "eliminated_players": [],
            "game_result": None,
            "last_update": time.time()
        })
        
        self._notify_callbacks(room_code, "reset")
        return True
    
    def cleanup_stale_rooms(self, max_age_hours=24):
        """
        Remove rooms that haven't been updated in the specified time.
        
        Args:
            max_age_hours (int): Maximum age in hours before a room is considered stale
            
        Returns:
            int: Number of rooms removed
        """
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        stale_rooms = []
        
        for room_code, room in self.game_rooms.items():
            if current_time - room["last_update"] > max_age_seconds:
                stale_rooms.append(room_code)
        
        for room_code in stale_rooms:
            del self.game_rooms[room_code]
            self._notify_callbacks(room_code, "cleanup")
        
        return len(stale_rooms)

# Create the singleton instance
_instance = GameState()

# Module-level functions that delegate to the singleton
def create_game_room(admin_name):
    return _instance.create_game_room(admin_name)

def join_game_room(room_code, player_name):
    return _instance.join_game_room(room_code, player_name)

def start_game(room_code, story_data):
    return _instance.start_game(room_code, story_data)

def set_admin_suspect(room_code, suspect_name):
    return _instance.set_admin_suspect(room_code, suspect_name)

def process_admin_accusation(room_code):
    return _instance.process_admin_accusation(room_code)

def get_player_info(room_code, player_name):
    return _instance.get_player_info(room_code, player_name)

def get_room_summary(room_code):
    return _instance.get_room_summary(room_code)

def reset_game(room_code):
    return _instance.reset_game(room_code)

def register_callback(callback_id, callback_fn):
    return _instance.register_callback(callback_id, callback_fn)

def unregister_callback(callback_id):
    return _instance.unregister_callback(callback_id)

def get_all_room_codes():
    return _instance.get_all_room_codes()

def cleanup_stale_rooms(max_age_hours=24):
    return _instance.cleanup_stale_rooms(max_age_hours) 