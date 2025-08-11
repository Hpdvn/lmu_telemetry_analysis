#!/usr/bin/env python3
"""
Script de test pour vérifier l'extraction de mTrackName et mVehicleName
"""

import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))

from rF2data import SimInfo, Cbytestring2Python, rFactor2Constants

def test_data_extraction():
    """Test l'extraction des données mTrackName et mVehicleName"""
    try:
        print("🔍 Test d'extraction des données rF2...")
        print("=" * 50)
        
        # Initialiser la connexion
        info = SimInfo()
        print("✅ Connexion à rF2 établie")
        
        # Test des données de scoring (pour mTrackName)
        print("\n📊 Données de scoring:")
        scoring_info = info.Rf2Scor.mScoringInfo
        track_name = Cbytestring2Python(scoring_info.mTrackName)
        session = scoring_info.mSession
        
        print(f"  🏁 Nom du circuit: '{track_name}'")
        print(f"  🏎️  Session actuelle: {session}")
        
        # Test des véhicules
        print("\n🚗 Recherche du véhicule joueur:")
        vehicles = info.Rf2Scor.mVehicles
        player_found = False
        
        for i in range(rFactor2Constants.MAX_MAPPED_VEHICLES):
            vehicle = vehicles[i]
            if vehicle.mIsPlayer == 1:
                player_found = True
                driver_name = Cbytestring2Python(vehicle.mDriverName)
                vehicle_name = Cbytestring2Python(vehicle.mVehicleName)
                
                print(f"  ✅ Véhicule joueur trouvé:")
                print(f"     👤 Pilote: '{driver_name}'")
                print(f"     🚗 Véhicule: '{vehicle_name}'")
                print(f"     🏆 Position: {vehicle.mPlace}")
                print(f"     🆔 ID: {vehicle.mID}")
                
                # Test des données de télémétrie
                print(f"\n📡 Données de télémétrie pour ID {vehicle.mID}:")
                telemetry_found = False
                
                for j in range(info.Rf2Tele.mNumVehicles):
                    tele = info.Rf2Tele.mVehicles[j]
                    if tele.mID == vehicle.mID:
                        telemetry_found = True
                        tele_vehicle_name = Cbytestring2Python(tele.mVehicleName)
                        tele_track_name = Cbytestring2Python(tele.mTrackName)
                        
                        print(f"  ✅ Télémétrie trouvée:")
                        print(f"     🚗 Véhicule (télémétrie): '{tele_vehicle_name}'")
                        print(f"     🏁 Circuit (télémétrie): '{tele_track_name}'")
                        print(f"     ⚙️  Vitesse: {tele.mGear}")
                        print(f"     🟢 Accélérateur: {tele.mFilteredThrottle:.2f}")
                        print(f"     🔴 Frein: {tele.mFilteredBrake:.2f}")
                        break
                
                if not telemetry_found:
                    print("  ❌ Aucune donnée de télémétrie trouvée")
                break
        
        if not player_found:
            print("  ❌ Aucun véhicule joueur trouvé")
            print("  💡 Assurez-vous d'être dans rFactor 2 avec une session active")
        
        print("\n" + "=" * 50)
        print("✅ Test terminé")
        
        # Résumé
        print(f"\n📋 Résumé:")
        print(f"  mTrackName (scoring): {'✅' if track_name else '❌'} '{track_name}'")
        if player_found:
            print(f"  mVehicleName (scoring): ✅ '{vehicle_name}'")
            if telemetry_found:
                print(f"  mTrackName (télémétrie): {'✅' if tele_track_name else '❌'} '{tele_track_name}'")
                print(f"  mVehicleName (télémétrie): {'✅' if tele_vehicle_name else '❌'} '{tele_vehicle_name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print("💡 Assurez-vous que rFactor 2 est lancé avec une session active")
        return False
    
    finally:
        try:
            info.close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Test d'extraction des données mTrackName et mVehicleName")
    print("Assurez-vous que rFactor 2 est lancé avec une session active...")
    
    input("Appuyez sur Entrée pour continuer...")
    
    success = test_data_extraction()
    
    if success:
        print("\n🎉 Test réussi ! Les données sont correctement extraites.")
    else:
        print("\n⚠️  Des problèmes ont été détectés dans l'extraction des données.")
    
    input("Appuyez sur Entrée pour quitter...")
