import asyncio
import json
from datetime import datetime
import time

class WebSocketManager:
    """
    A manager for WebSocket connections to enable real-time updates
    This can be used with frameworks like FastAPI, Flask-SocketIO, or other websocket solutions
    """
    def __init__(self):
        self.active_connections = {}  # room_code -> [connection1, connection2, ...]
        self.connection_rooms = {}  # connection_id -> room_code
    
    def register_connection(self, connection_id, room_code, connection_object):
        """
        Register a new WebSocket connection for a specific room
        
        Args:
            connection_id (str): Unique identifier for this connection
            room_code (str): The room code this connection is interested in
            connection_object: The websocket connection object (framework specific)
        """
        if room_code not in self.active_connections:
            self.active_connections[room_code] = {}
        
        self.active_connections[room_code][connection_id] = connection_object
        self.connection_rooms[connection_id] = room_code
    
    def unregister_connection(self, connection_id):
        """
        Remove a WebSocket connection
        
        Args:
            connection_id (str): Unique identifier for this connection
        """
        if connection_id in self.connection_rooms:
            room_code = self.connection_rooms[connection_id]
            if room_code in self.active_connections:
                if connection_id in self.active_connections[room_code]:
                    del self.active_connections[room_code][connection_id]
                
                # Clean up empty rooms
                if not self.active_connections[room_code]:
                    del self.active_connections[room_code]
            
            del self.connection_rooms[connection_id]
    
    async def broadcast_to_room(self, room_code, message):
        """
        Broadcast a message to all connections in a room
        
        Args:
            room_code (str): The room code to broadcast to
            message (dict): The message to broadcast
        """
        if room_code not in self.active_connections:
            return
        
        # Add timestamp to the message
        message["timestamp"] = time.time()
        message_json = json.dumps(message)
        
        disconnect_list = []
        
        for connection_id, connection in self.active_connections[room_code].items():
            try:
                # This is where you would send the message based on your WebSocket framework
                # For example, with FastAPI:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error sending to connection {connection_id}: {e}")
                disconnect_list.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnect_list:
            self.unregister_connection(connection_id)
    
    def get_connection_count(self, room_code=None):
        """
        Get the number of active connections
        
        Args:
            room_code (str, optional): If provided, count connections for this room only
            
        Returns:
            int: Number of active connections
        """
        if room_code:
            if room_code in self.active_connections:
                return len(self.active_connections[room_code])
            return 0
        else:
            return len(self.connection_rooms)

# Create singleton instance
_websocket_manager = WebSocketManager()

# Export the singleton
def get_websocket_manager():
    return _websocket_manager

# Callback function for game state changes
def game_state_callback(room_code, event_type):
    """
    Callback function to notify connected clients of game state changes
    
    Args:
        room_code (str): The room code where the event occurred
        event_type (str): The type of event that occurred
    """
    message = {
        "event": event_type,
        "room_code": room_code
    }
    
    # Use asyncio to run the async broadcast function
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(_websocket_manager.broadcast_to_room(room_code, message))
    else:
        loop.run_until_complete(_websocket_manager.broadcast_to_room(room_code, message))


# ==========================================================================
# FastAPI WebSocket Integration Example 
# ==========================================================================
"""
To use with FastAPI, you would implement something like:

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from uuid import uuid4

app = FastAPI()
websocket_manager = get_websocket_manager()

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await websocket.accept()
    
    # Generate a unique ID for this connection
    connection_id = str(uuid4())
    
    # Register this connection
    websocket_manager.register_connection(connection_id, room_code, websocket)
    
    try:
        # Send initial state
        from utils.game_state import get_room_summary
        room_summary = get_room_summary(room_code)
        if room_summary:
            await websocket.send_json({
                "event": "initial_state",
                "data": room_summary
            })
        
        # Listen for messages (if needed)
        while True:
            data = await websocket.receive_text()
            # Process any client messages if needed
    
    except WebSocketDisconnect:
        # Clean up on disconnect
        websocket_manager.unregister_connection(connection_id)
"""

# ==========================================================================
# Socket.IO Integration Example
# ==========================================================================
"""
To use with Flask-SocketIO, you would implement something like:

from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    room_code = data.get('room_code')
    if room_code:
        join_room(room_code)
        websocket_manager.register_connection(request.sid, room_code, request.sid)
        
        # Send initial state
        from utils.game_state import get_room_summary
        room_summary = get_room_summary(room_code)
        if room_summary:
            socketio.emit('update', {
                "event": "initial_state",
                "data": room_summary
            }, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    websocket_manager.unregister_connection(request.sid)
""" 