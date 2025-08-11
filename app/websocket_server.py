#!/usr/bin/env python3
"""
Python WebSocket server for rFactor 2 telemetry data
Equivalent to the Go implementation in main.go
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any
import websockets
from websockets.server import WebSocketServerProtocol

# Import our rF2 data structures
from rF2data import SimInfo, Cbytestring2Python, rFactor2Constants

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TelemetryResponse:
    """Data structure for WebSocket response, equivalent to Go's TelemetryResponse"""
    
    def __init__(self, driver_name: str, vehicle_name: str, track_name: str, place: int, 
                 gear: int, brake: float, throttle: float, session: int):
        self.driver_name = driver_name
        self.vehicle_name = vehicle_name
        self.track_name = track_name
        self.place = place
        self.gear = gear
        self.brake = brake
        self.throttle = throttle
        self.session = session
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "driverName": self.driver_name,
            "vehicleName": self.vehicle_name,
            "trackName": self.track_name,
            "place": self.place,
            "gear": self.gear,
            "brake": self.brake,
            "throttle": self.throttle,
            "session": self.session
        }


class RF2WebSocketServer:
    """WebSocket server for rFactor 2 telemetry data"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.sim_info: Optional[SimInfo] = None
        self.active_connections = set()
        
    async def initialize_sim_info(self) -> bool:
        """Initialize connection to rF2 shared memory"""
        try:
            self.sim_info = SimInfo()
            logger.info("Successfully connected to rF2 shared memory")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to rF2 shared memory: {e}")
            return False
    
    def find_player_vehicle(self):
        """Find the player vehicle from scoring data, equivalent to Go's findPlayerVehicleID"""
        if not self.sim_info or not self.sim_info.Rf2Scor:
            logger.error("No scoring data found")
            return None, -1
        
        vehicles = self.sim_info.Rf2Scor.mVehicles
        for i in range(rFactor2Constants.MAX_MAPPED_VEHICLES):
            vehicle = vehicles[i]
            logger.debug(f"Vehicle: {vehicle.mID}, {vehicle.mIsPlayer}, {Cbytestring2Python(vehicle.mDriverName)}, {Cbytestring2Python(vehicle.mVehicleName)}")
            # Check if this slot has a valid vehicle and if it's the player vehicle
            if vehicle.mIsPlayer == 1:
                return vehicle, vehicle.mID
        
        return None, -1
    
    def find_player_telemetry(self, player_id: int):
        """Find telemetry data for player vehicle by matching ID, equivalent to Go's findPlayerTelemetry"""
        if not self.sim_info or not self.sim_info.Rf2Tele:
            return None
        
        num_vehicles = self.sim_info.Rf2Tele.mNumVehicles
        vehicles = self.sim_info.Rf2Tele.mVehicles
        
        for i in range(min(num_vehicles, rFactor2Constants.MAX_MAPPED_VEHICLES)):
            if vehicles[i].mID == player_id:
                return vehicles[i]
        
        return None
    
    def get_telemetry_data(self) -> Optional[TelemetryResponse]:
        """Get current telemetry data for the player vehicle"""
        try:
            # Find the player vehicle from scoring data
            player_vehicle, player_vehicle_id = self.find_player_vehicle()
            if player_vehicle_id == -1:
                logger.debug("No player vehicle found")
                return None
            
            # Get data from scoring
            driver_name = Cbytestring2Python(player_vehicle.mDriverName)
            vehicle_name = Cbytestring2Python(player_vehicle.mVehicleName)
            track_name = Cbytestring2Python(self.sim_info.Rf2Scor.mScoringInfo.mTrackName)
            place = player_vehicle.mPlace
            session = self.sim_info.Rf2Scor.mScoringInfo.mSession
            
            # Find corresponding telemetry data
            player_telemetry = self.find_player_telemetry(player_vehicle_id)
            if player_telemetry is None:
                logger.debug(f"No telemetry data found for player vehicle ID: {player_vehicle_id}")
                return None
            
            # Get telemetry data
            gear = player_telemetry.mGear
            throttle = player_telemetry.mFilteredThrottle
            brake = player_telemetry.mFilteredBrake
            
            return TelemetryResponse(
                driver_name=driver_name,
                vehicle_name=vehicle_name,
                track_name=track_name,
                place=place,
                gear=gear,
                brake=brake,
                throttle=throttle,
                session=session
            )
            
        except Exception as e:
            logger.error(f"Error getting telemetry data: {e}")
            return None
    
    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle WebSocket client connection, equivalent to Go's wsHandler"""
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"New WebSocket connection from {client_address}")
        
        # Add to active connections
        self.active_connections.add(websocket)
        
        try:
            # Send data every 1000ms (1 second) like in the Go version
            while True:
                telemetry_data = self.get_telemetry_data()
                
                if telemetry_data:
                    # Convert to JSON and send
                    json_data = json.dumps(telemetry_data.to_dict())
                    logger.info(json_data)  # Log the data like in Go version
                    
                    await websocket.send(json_data)
                else:
                    # Send empty data or status message if no player found
                    status_msg = json.dumps({"status": "no_player_vehicle_found"})
                    await websocket.send(status_msg)
                
                # Wait 1 second before next update (equivalent to Go's ticker)
                await asyncio.sleep(0.1)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for {client_address}")
        except Exception as e:
            logger.error(f"Error in WebSocket handler for {client_address}: {e}")
        finally:
            # Remove from active connections
            self.active_connections.discard(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        # Initialize connection to rF2
        if not await self.initialize_sim_info():
            logger.error("Failed to initialize rF2 connection. Make sure rFactor 2 is running.")
            return
        
        # Start WebSocket server
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}/ws")
        
        async with websockets.serve(
            self.handle_client, 
            self.host, 
            self.port,
            subprotocols=[]  # Allow all origins like in Go version
        ):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            # Keep the server running indefinitely
            await asyncio.Future()  # Run forever
    
    def cleanup(self):
        """Cleanup resources"""
        if self.sim_info:
            self.sim_info.close()
            logger.info("Closed rF2 shared memory connection")


async def main():
    """Main function to start the server"""
    server = RF2WebSocketServer(host="localhost", port=8080)
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.cleanup()


if __name__ == "__main__":
    print("rFactor 2 WebSocket Server")
    print("==========================")
    print("Make sure rFactor 2 is running before starting this server.")
    print("Server will be available at: ws://localhost:8080")
    print("Press Ctrl+C to stop the server")
    print()
    
    asyncio.run(main())
