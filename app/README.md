# Le Mans Ultimate WebSocket Server (Python)

This Python WebSocket server provides real-time LMU telemetry data.

## Prerequisites

- **Python 3.7+** (required for asyncio and websockets)
- **Le Mans Ultimate** running
- **Windows** (for rF2 shared memory access)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. **Launch LMU** and load a session (practice, qualify, or race)

2. **Start the WebSocket server**:
```bash
python websocket_server.py
```

3. The server will be available at: `ws://localhost:8080/ws`

## Features

The server sends the following JSON data every second:

```json
{
  "driverName": "Hugo PDVN",
  "vehicleName": "Manthey 2025 #90:LM", 
  "trackName": "Le Mans 2025",
  "place": 16, //(1-based)
  "gear": 1, //(-1=reverse, 0=neutral, 1+=forward gears)
  "brake": 0.0, //(0.0-1.0)
  "throttle": 0.3756, //(0.0-1.0)
  "session": 10
}
```

## Testing the server

You can test the server with a simple WebSocket client. Example with JavaScript in the browser:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = function() {
    console.log('Connected to rF2 WebSocket server');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Data received:', data);
};

ws.onclose = function() {
    console.log('Connection closed');
};
```

## Display

You can use whatever frontend you would like to use to display all the data. A simple one is provided at the root of the repo.

## Development

To modify the server:

1. **Add new data**: Modify the `TelemetryResponse` class and the `get_telemetry_data()` method based on the `rF2data.py` file
2. **Change frequency**: Modify the value in `await asyncio.sleep(1.0)`
3. **Modify port**: Change the default value in `RF2WebSocketServer()`

## License

This code uses rF2 data structures from https://github.com/TonyWhitley/pyRfactor2SharedMemory
