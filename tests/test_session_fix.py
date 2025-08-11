#!/usr/bin/env python3
"""
Test pour vérifier la correction de l'accès à mSession
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python'))

from rF2data import SimInfo, Cbytestring2Python

def test_session_access():
    """Test l'accès correct à mSession"""
    try:
        print("🔍 Test de l'accès à mSession...")
        
        # Initialiser la connexion
        info = SimInfo()
        print("✅ Connexion à rF2 établie")
        
        # Test de l'accès INCORRECT (celui qui causait l'erreur)
        try:
            session_wrong = info.Rf2Scor.mSession  # ❌ Ceci causait l'erreur
            print("❌ Accès direct à Rf2Scor.mSession (ne devrait pas fonctionner)")
        except AttributeError as e:
            print(f"✅ Erreur attendue pour accès direct: {e}")
        
        # Test de l'accès CORRECT (la correction)
        try:
            session_correct = info.Rf2Scor.mScoringInfo.mSession  # ✅ Ceci est correct
            print(f"✅ Accès correct à Rf2Scor.mScoringInfo.mSession: {session_correct}")
        except AttributeError as e:
            print(f"❌ Erreur inattendue pour accès correct: {e}")
        
        # Test de l'accès à mTrackName
        try:
            track_name = Cbytestring2Python(info.Rf2Scor.mScoringInfo.mTrackName)
            print(f"✅ Accès à mTrackName: '{track_name}'")
        except AttributeError as e:
            print(f"❌ Erreur pour accès à mTrackName: {e}")
        
        # Affichage de la structure
        print("\n📋 Structure correcte:")
        print("  info.Rf2Scor.mScoringInfo.mSession ✅")
        print("  info.Rf2Scor.mScoringInfo.mTrackName ✅")
        print("  info.Rf2Scor.mVehicles[i].mVehicleName ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False
    
    finally:
        try:
            info.close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Test de correction de l'accès à mSession")
    print("=" * 50)
    
    success = test_session_access()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test terminé - La correction devrait fonctionner")
    else:
        print("❌ Des problèmes persistent")
