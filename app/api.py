from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import math
import csv
import os
from datetime import datetime
from rF2data import SimInfo

app = FastAPI(title="LMU Telemetry API", description="API for LMU telemetry data")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_total_acceleration(local_accel):
    """Calculate total acceleration magnitude from 3D acceleration vector"""
    try:
        # Calculate magnitude from x, y, z components
        total_accel = math.sqrt(local_accel.x**2 + local_accel.y**2 + local_accel.z**2)
        return total_accel
    except:
        return 0.0

def calculate_forward_acceleration(local_accel):
    """Calculate forward/backward acceleration (longitudinal)"""
    try:
        # Z component typically represents forward/backward acceleration
        return local_accel.z
    except:
        return 0.0

# Pydantic models for export data
class TelemetryDataPoint(BaseModel):
    timestamp: str
    session: int
    gear: int
    brake: float
    throttle: float
    driverName: str
    vehicleName: str
    trackName: str
    place: int

class SessionInfo(BaseModel):
    currentSession: int
    totalPoints: int
    startTime: str
    endTime: str

class ExportRequest(BaseModel):
    data: List[TelemetryDataPoint]
    sessionInfo: SessionInfo

@app.get("/data")
def get_telemetry_data():
    """
    Get comprehensive telemetry data including acceleration and braking
    Returns: JSON with acceleration, braking, clutch, gear, and additional telemetry
    """
    try:
        info = SimInfo()
        vehicle = info.Rf2Tele.mVehicles[0]
        
        # Basic controls
        clutch = float(vehicle.mUnfilteredClutch)  # 1.0 clutch down, 0 clutch up
        gear = int(vehicle.mGear)  # -1 reverse, 0 neutral, 1+ forward gears
        brake = float(vehicle.mUnfilteredBrake)  # 0.0-1.0 brake pedal position
        throttle = float(vehicle.mUnfilteredThrottle)  # 0.0-1.0 throttle pedal position
        
        # Acceleration data
        total_acceleration = calculate_total_acceleration(vehicle.mLocalAccel)
        forward_acceleration = calculate_forward_acceleration(vehicle.mLocalAccel)
        
        # For dashboard compatibility, use throttle as "acceleration" 
        # since it represents driver input acceleration intent
        acceleration = throttle
        
        # Additional useful telemetry
        engine_rpm = float(vehicle.mEngineRPM)
        speed_ms = math.sqrt(vehicle.mLocalVel.x**2 + vehicle.mLocalVel.y**2 + vehicle.mLocalVel.z**2)
        speed_kmh = speed_ms * 3.6
        
        response_data = {
            "brake": brake,
            "acceleration": acceleration,  # Throttle position for dashboard
            "clutch": clutch,
            "gear": gear,
            "throttle": throttle,
            "engine_rpm": engine_rpm,
            "speed_kmh": speed_kmh,
            "speed_ms": speed_ms,
            "total_acceleration_ms2": total_acceleration,
            "forward_acceleration_ms2": forward_acceleration,
            "acceleration_vector": {
                "x": float(vehicle.mLocalAccel.x),
                "y": float(vehicle.mLocalAccel.y), 
                "z": float(vehicle.mLocalAccel.z)
            },
            "velocity_vector": {
                "x": float(vehicle.mLocalVel.x),
                "y": float(vehicle.mLocalVel.y),
                "z": float(vehicle.mLocalVel.z)
            }
        }
        
        print(f'Gear: {gear}, Brake: {brake:.2f}, Acceleration: {acceleration:.2f}, RPM: {engine_rpm:.0f}')
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error reading telemetry data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read telemetry data: {str(e)}")

@app.get("/acceleration")
def get_acceleration_data():
    """
    Get detailed acceleration data only
    Returns: JSON with various acceleration metrics
    """
    try:
        info = SimInfo()
        vehicle = info.Rf2Tele.mVehicles[0]
        
        total_acceleration = calculate_total_acceleration(vehicle.mLocalAccel)
        forward_acceleration = calculate_forward_acceleration(vehicle.mLocalAccel)
        throttle = float(vehicle.mUnfilteredThrottle)
        
        return JSONResponse(content={
            "throttle_position": throttle,
            "total_acceleration_ms2": total_acceleration,
            "forward_acceleration_ms2": forward_acceleration,
            "lateral_acceleration_ms2": float(vehicle.mLocalAccel.x),
            "vertical_acceleration_ms2": float(vehicle.mLocalAccel.y),
            "acceleration_vector": {
                "x": float(vehicle.mLocalAccel.x),
                "y": float(vehicle.mLocalAccel.y),
                "z": float(vehicle.mLocalAccel.z)
            }
        })
        
    except Exception as e:
        print(f"Error reading acceleration data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read acceleration data: {str(e)}")

@app.get("/braking")
def get_braking_data():
    """
    Get detailed braking data only
    Returns: JSON with braking metrics and related data
    """
    try:
        info = SimInfo()
        vehicle = info.Rf2Tele.mVehicles[0]
        
        brake = float(vehicle.mUnfilteredBrake)
        brake_filtered = float(vehicle.mFilteredBrake)
        
        # Get brake temperatures and pressures from wheels
        brake_temps = [float(vehicle.mWheels[i].mBrakeTemp) for i in range(4)]
        brake_pressures = [float(vehicle.mWheels[i].mBrakePressure) for i in range(4)]
        
        return JSONResponse(content={
            "brake_position": brake,
            "brake_filtered": brake_filtered,
            "brake_temperatures": {
                "front_left": brake_temps[0],
                "front_right": brake_temps[1], 
                "rear_left": brake_temps[2],
                "rear_right": brake_temps[3]
            },
            "brake_pressures": {
                "front_left": brake_pressures[0],
                "front_right": brake_pressures[1],
                "rear_left": brake_pressures[2], 
                "rear_right": brake_pressures[3]
            },
            "rear_brake_bias": float(vehicle.mRearBrakeBias)
        })
        
    except Exception as e:
        print(f"Error reading braking data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read braking data: {str(e)}")

@app.post("/export-csv")
async def export_telemetry_csv(request: ExportRequest):
    """
    Export telemetry data to CSV file
    """
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver_name = request.data[0].driverName.replace(" ", "_") if request.data else "unknown"
        vehicle_name = request.data[0].vehicleName.replace(" ", "_") if request.data else "unknown"
        track_name = request.sessionInfo.trackName.replace(" ", "_") if request.sessionInfo else "unknown"
        filename = f"telemetry_{driver_name}_{track_name}_{vehicle_name}_{timestamp}.csv"
        filepath = os.path.join("export", filename)
        
        # Ensure export directory exists
        os.makedirs("export", exist_ok=True)
        
        # Define CSV headers
        headers = [
            "timestamp", "session", "session_name", "gear", "brake_percent", 
            "throttle_percent", "driver_name", "vehicle_name", "track_name", "place"
        ]
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for point in request.data:
                # Convert session number to readable name
                session_name = get_session_name(point.session)
                
                writer.writerow([
                    point.timestamp,
                    point.session,
                    session_name,
                    point.gear,
                    round(point.brake * 100, 2),  # Convert to percentage
                    round(point.throttle * 100, 2),  # Convert to percentage
                    point.driverName,
                    point.vehicleName,
                    point.trackName,
                    point.place
                ])
        
        return JSONResponse(content={
            "success": True,
            "message": "CSV export successful",
            "filename": filename,
            "filepath": filepath,
            "total_points": len(request.data),
            "session_info": {
                "start_time": request.sessionInfo.startTime,
                "end_time": request.sessionInfo.endTime,
                "current_session": request.sessionInfo.currentSession
            }
        })
        
    except Exception as e:
        print(f"Error during CSV export: {e}")
        raise HTTPException(status_code=500, detail=f"Error during CSV export: {str(e)}")

def get_session_name(session: int) -> str:
    """Convert session number to readable name"""
    if session == 0:
        return "Test"
    elif 1 <= session <= 4:
        return f"Practice_{session}"
    elif 5 <= session <= 8:
        return f"Qualifying_{session - 4}"
    elif session == 9:
        return "Warmup"
    elif 10 <= session <= 13:
        return f"Race_{session - 9}"
    else:
        return f"Unknown_{session}"

@app.get("/")
def root():
    """API information and available endpoints"""
    return {
        "message": "LMU Telemetry API",
        "version": "2.1",
        "endpoints": {
            "/data": "Complete telemetry data (acceleration, braking, gear, etc.)",
            "/acceleration": "Detailed acceleration data only", 
            "/braking": "Detailed braking data only",
            "/export-csv": "Export telemetry data to CSV (POST)",
            "/docs": "Interactive API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
