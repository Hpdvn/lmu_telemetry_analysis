# rFactor 2 WebSocket Server (Python)

Ce serveur WebSocket Python fournit les données de télémétrie rFactor 2 en temps réel, équivalent à l'implémentation Go.

## Prérequis

- **Python 3.7+** (requis pour asyncio et websockets)
- **rFactor 2** en cours d'exécution
- **Windows** (pour l'accès à la mémoire partagée rF2)

## Installation

1. Installez les dépendances :
```bash
pip install -r requirements.txt
```

Ou installez manuellement :
```bash
pip install websockets>=12.0
```

## Utilisation

1. **Lancez rFactor 2** et chargez une session (practice, qualify, ou race)

2. **Démarrez le serveur WebSocket** :
```bash
python websocket_server.py
```

3. Le serveur sera disponible à l'adresse : `ws://localhost:8080`

## Fonctionnalités

Le serveur envoie les données JSON suivantes toutes les secondes :

```json
{
  "driverName": "Nom du pilote",
  "vehicleName": "Nom du véhicule", 
  "place": 1,
  "gear": 3,
  "brake": 0.0,
  "throttle": 0.85
}
```

### Données disponibles :
- **driverName** : Nom du pilote
- **vehicleName** : Nom du véhicule
- **place** : Position dans la course (1-based)
- **gear** : Vitesse engagée (-1=marche arrière, 0=neutre, 1+=vitesses avant)
- **brake** : Pression de frein (0.0-1.0)
- **throttle** : Position de l'accélérateur (0.0-1.0)

## Test du serveur

Vous pouvez tester le serveur avec un client WebSocket simple. Exemple avec JavaScript dans le navigateur :

```javascript
const ws = new WebSocket('ws://localhost:8080');

ws.onopen = function() {
    console.log('Connecté au serveur WebSocket rF2');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Données reçues:', data);
};

ws.onclose = function() {
    console.log('Connexion fermée');
};
```

## Architecture

Le serveur Python suit la même architecture que la version Go :

1. **SimInfo** : Connexion à la mémoire partagée rF2
2. **find_player_vehicle()** : Recherche du véhicule joueur dans les données de scoring
3. **find_player_telemetry()** : Récupération des données de télémétrie correspondantes
4. **WebSocket Handler** : Envoi des données JSON toutes les secondes

## Dépannage

### "Failed to connect to rF2 shared memory"
- Vérifiez que rFactor 2 est lancé
- Assurez-vous d'être dans une session active (pas seulement dans les menus)
- Vérifiez que vous êtes sur Windows (la mémoire partagée rF2 n'est disponible que sur Windows)

### "No player vehicle found"
- Assurez-vous d'être dans une session avec un véhicule (practice, qualify, race)
- Vérifiez que vous contrôlez effectivement un véhicule dans le jeu

### Erreurs de connexion WebSocket
- Vérifiez que le port 8080 n'est pas utilisé par une autre application
- Testez avec un client WebSocket simple pour vérifier la connectivité

## Comparaison avec la version Go

Cette implémentation Python est fonctionnellement équivalente à la version Go :

| Fonctionnalité | Go | Python |
|----------------|-------|--------|
| Serveur WebSocket | ✅ | ✅ |
| Accès mémoire partagée | ✅ | ✅ |
| Mise à jour 1Hz | ✅ | ✅ |
| Données JSON identiques | ✅ | ✅ |
| Gestion multi-clients | ✅ | ✅ |

## Développement

Pour modifier le serveur :

1. **Ajouter de nouvelles données** : Modifiez la classe `TelemetryResponse` et la méthode `get_telemetry_data()`
2. **Changer la fréquence** : Modifiez la valeur dans `await asyncio.sleep(1.0)`
3. **Modifier le port** : Changez la valeur par défaut dans `RF2WebSocketServer()`

## Licence

Ce code utilise les structures de données rF2 de The Iron Wolf's rF2 Shared Memory Tools.
