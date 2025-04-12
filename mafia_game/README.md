# Mafia Game

A multiplayer social deduction game where players work together to identify the killer among them.

## Features

- Create and join game rooms with unique room codes
- AI-generated murder mystery stories with characters and clues
- Real-time game state updates
- Admin controls for game management
- Offline discussion mode for player interaction

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following:

```
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=your_preferred_model
```

## Running the Game

To run the standard Streamlit version of the game:

```bash
cd mafia_game
streamlit run app.py
```

## Fixing Refresh Issues

The game now uses several mechanisms to ensure reliable real-time updates:

1. **Smart refresh detection** - The application only refreshes when there are actual changes to the game state
2. **Client-side JavaScript polling** - A lightweight polling mechanism keeps the connection alive
3. **Time-based timestamps** - Game state changes are tracked with timestamps for better consistency
4. **Manual refresh buttons** - Players can manually refresh their view if needed

## WebSocket Integration for Real-Time Updates

For a more responsive experience, you can integrate WebSockets using the provided handlers. The codebase includes ready-to-use WebSocket integration with examples for FastAPI and Socket.IO.

### Using FastAPI WebSockets

1. Create a new file `websocket_server.py` in the project root:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uuid import uuid4
import asyncio

from mafia_game.utils.socket_handler import get_websocket_manager
from mafia_game.utils.game_state import register_callback, get_room_summary

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

websocket_manager = get_websocket_manager()

# Register the callback to broadcast game state changes
from mafia_game.utils.socket_handler import game_state_callback
register_callback("fastapi_server", game_state_callback)

@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await websocket.accept()
    
    # Generate a unique ID for this connection
    connection_id = str(uuid4())
    
    # Register this connection
    websocket_manager.register_connection(connection_id, room_code, websocket)
    
    try:
        # Send initial state
        room_summary = get_room_summary(room_code)
        if room_summary:
            await websocket.send_json({
                "event": "initial_state",
                "data": room_summary
            })
        
        # Keep connection alive
        while True:
            await asyncio.sleep(10)
            await websocket.send_json({"event": "ping"})
    
    except WebSocketDisconnect:
        websocket_manager.unregister_connection(connection_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

2. Install the required packages:

```bash
pip install fastapi uvicorn
```

3. Run the WebSocket server:

```bash
python websocket_server.py
```

4. Connect from your client application:

```javascript
// Client-side JavaScript
const socket = new WebSocket(`ws://localhost:8000/ws/${roomCode}`);

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === "ping") return;
    
    console.log("Game update:", data);
    // Update your UI based on the received event
    if (data.event === "initial_state") {
        // Initialize game state
    } else if (data.event === "join" || data.event === "create") {
        // Refresh player list
    } else if (data.event === "start" || data.event === "next_round") {
        // Update game state and UI
    }
};
```

### Using Socket.IO

1. Create a new file `socketio_server.py` in the project root:

```python
from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room
from flask_cors import CORS

from mafia_game.utils.socket_handler import get_websocket_manager
from mafia_game.utils.game_state import register_callback, get_room_summary, unregister_callback

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

websocket_manager = get_websocket_manager()

# Custom callback for Socket.IO
def socketio_callback(room_code, event_type):
    socketio.emit('update', {
        'event': event_type,
        'room_code': room_code,
        'timestamp': import time; time.time()
    }, room=room_code)

# Register the callback
register_callback("socketio_server", socketio_callback)

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
        room_summary = get_room_summary(room_code)
        if room_summary:
            socketio.emit('update', {
                "event": "initial_state",
                "data": room_summary
            }, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    websocket_manager.unregister_connection(request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

2. Install the required packages:

```bash
pip install flask flask-socketio flask-cors
```

3. Run the Socket.IO server:

```bash
python socketio_server.py
```

4. Connect from your client application:

```javascript
// Client-side JavaScript with Socket.IO
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    socket.emit('join', { room_code: 'YOUR_ROOM_CODE' });
});

socket.on('update', (data) => {
    console.log('Game update:', data);
    // Update your UI based on the received event
});
```

## Creating a Frontend App with Real-Time Updates

You can create a custom frontend application using React, Vue, or any other framework that connects to the WebSocket server for real-time updates. The game state API provides all the necessary endpoints for game management.

## Architecture

The application is structured as follows:

- `app.py` - Main Streamlit application
- `utils/` - Core functionality
  - `game_state.py` - Game state management
  - `openrouter.py` - AI story generation
  - `storyteller.py` - Story formatting
  - `socket_handler.py` - WebSocket integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 