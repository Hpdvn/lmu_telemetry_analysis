#!/usr/bin/env python3
"""
Vérification des structures de données rF2
"""

from rF2data import rF2ScoringInfo, rF2VehicleTelemetry, rF2VehicleScoring
import ctypes

def verify_structures():
    """Vérifie que les structures contiennent bien mTrackName et mVehicleName"""
    print("🔍 Vérification des structures de données rF2")
    print("=" * 60)
    
    # Vérification rF2ScoringInfo
    print("\n📊 Structure rF2ScoringInfo:")
    scoring_fields = [field[0] for field in rF2ScoringInfo._fields_]
    print(f"  mTrackName présent: {'✅' if 'mTrackName' in scoring_fields else '❌'}")
    print(f"  mSession présent: {'✅' if 'mSession' in scoring_fields else '❌'}")
    
    # Vérification rF2VehicleTelemetry
    print("\n📡 Structure rF2VehicleTelemetry:")
    tele_fields = [field[0] for field in rF2VehicleTelemetry._fields_]
    print(f"  mVehicleName présent: {'✅' if 'mVehicleName' in tele_fields else '❌'}")
    print(f"  mTrackName présent: {'✅' if 'mTrackName' in tele_fields else '❌'}")
    print(f"  mGear présent: {'✅' if 'mGear' in tele_fields else '❌'}")
    print(f"  mFilteredBrake présent: {'✅' if 'mFilteredBrake' in tele_fields else '❌'}")
    print(f"  mFilteredThrottle présent: {'✅' if 'mFilteredThrottle' in tele_fields else '❌'}")
    
    # Vérification rF2VehicleScoring
    print("\n🏆 Structure rF2VehicleScoring:")
    scoring_veh_fields = [field[0] for field in rF2VehicleScoring._fields_]
    print(f"  mVehicleName présent: {'✅' if 'mVehicleName' in scoring_veh_fields else '❌'}")
    print(f"  mDriverName présent: {'✅' if 'mDriverName' in scoring_veh_fields else '❌'}")
    print(f"  mIsPlayer présent: {'✅' if 'mIsPlayer' in scoring_veh_fields else '❌'}")
    print(f"  mPlace présent: {'✅' if 'mPlace' in scoring_veh_fields else '❌'}")
    
    print("\n" + "=" * 60)
    print("✅ Vérification terminée")
    
    # Types des champs
    print(f"\n📋 Types des champs:")
    for name, field_type in rF2ScoringInfo._fields_:
        if name in ['mTrackName', 'mSession']:
            print(f"  rF2ScoringInfo.{name}: {field_type}")
    
    for name, field_type in rF2VehicleTelemetry._fields_:
        if name in ['mVehicleName', 'mTrackName']:
            print(f"  rF2VehicleTelemetry.{name}: {field_type}")
    
    for name, field_type in rF2VehicleScoring._fields_:
        if name in ['mVehicleName', 'mDriverName']:
            print(f"  rF2VehicleScoring.{name}: {field_type}")

if __name__ == "__main__":
    verify_structures()
