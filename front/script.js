const WS_URL = "ws://localhost:8080/ws";

let sock;
const statusEl = document.getElementById('status');
const gearValueEl = document.getElementById('gearValue');
const gearDescriptionEl = document.getElementById('gearDescription');
const brakeValueEl = document.getElementById('brakeValue');
const brakeFillEl = document.getElementById('brakeFill');
const throttleValueEl = document.getElementById('throttleValue');
const throttleFillEl = document.getElementById('throttleFill');
const sessionValueEl = document.getElementById('sessionValue');
const sessionDescriptionEl = document.getElementById('sessionDescription');
const trackValueEl = document.getElementById('trackValue');
const vehicleValueEl = document.getElementById('vehicleValue');

// Smoothie Charts setup
let brakeChart, throttleChart;
let brakeTimeSeries, throttleTimeSeries;
let startTime;

// Data collection for export
let telemetryData = [];
let isCollectingData = false;
let currentSession = null;

function initializeCharts() {
  startTime = Date.now();
  
  // Verify canvas elements exist and have proper dimensions
  const brakeCanvas = document.getElementById('brakeChart');
  const throttleCanvas = document.getElementById('throttleChart');
  
  if (!brakeCanvas || !throttleCanvas) {
    console.error('Canvas elements not found!');
    return;
  }
  
  // Set explicit dimensions
  brakeCanvas.width = brakeCanvas.offsetWidth;
  brakeCanvas.height = brakeCanvas.offsetHeight;
  throttleCanvas.width = throttleCanvas.offsetWidth;
  throttleCanvas.height = throttleCanvas.offsetHeight;
  
  console.log('Canvas dimensions:', {
    brake: { width: brakeCanvas.width, height: brakeCanvas.height },
    throttle: { width: throttleCanvas.width, height: throttleCanvas.height }
  });
  
  // Initialize brake chart - simplified like the working example
  brakeChart = new SmoothieChart();
  brakeTimeSeries = new TimeSeries();
  brakeChart.addTimeSeries(brakeTimeSeries, { 
    strokeStyle: 'rgba(239, 68, 68, 1)', 
    fillStyle: 'rgba(239, 68, 68, 0.2)', 
    lineWidth: 3 
  });
  
  // Initialize throttle chart - simplified like the working example
  throttleChart = new SmoothieChart();
  throttleTimeSeries = new TimeSeries();
  throttleChart.addTimeSeries(throttleTimeSeries, { 
    strokeStyle: 'rgba(16, 185, 129, 1)', 
    fillStyle: 'rgba(16, 185, 129, 0.2)', 
    lineWidth: 3 
  });
  
  // Start the charts using canvas IDs like the working example
  brakeChart.streamTo(document.getElementById("brakeChart"), 100);
  throttleChart.streamTo(document.getElementById("throttleChart"), 100);
  
  // Add test data using absolute timestamps like the working example
  setTimeout(() => {
    brakeTimeSeries.append(Date.now(), 25);
    throttleTimeSeries.append(Date.now(), 30);
    console.log('Test data added to charts');
    
    setTimeout(() => {
      brakeTimeSeries.append(Date.now(), 40);
      throttleTimeSeries.append(Date.now(), 60);
      
      setTimeout(() => {
        brakeTimeSeries.append(Date.now(), 15);
        throttleTimeSeries.append(Date.now(), 80);
        console.log('Additional test data added');
      }, 200);
    }, 200);
  }, 100);
  
  console.log('Charts initialized successfully');
}

function updateGearDisplay(gear) {
  // Réinitialiser les classes CSS
  gearValueEl.className = 'gear-display';
  
  if (gear === -1) {
    gearValueEl.textContent = 'R';
    gearValueEl.classList.add('reverse');
    gearDescriptionEl.textContent = 'Marche arrière';
  } else if (gear === 0) {
    gearValueEl.textContent = 'N';
    gearValueEl.classList.add('neutral');
    gearDescriptionEl.textContent = 'Point mort';
  } else if (gear > 0) {
    gearValueEl.textContent = gear.toString();
    gearDescriptionEl.textContent = `${gear}${gear === 1 ? 'ère' : 'ème'} vitesse`;
  } else {
    gearValueEl.textContent = '?';
    gearDescriptionEl.textContent = 'Valeur inconnue';
  }
}

function updateBrakeDisplay(brake) {
  // Convertir en pourcentage et limiter à 100%
  const percentage = Math.min(Math.max(brake * 100, 0), 100);
  brakeValueEl.textContent = `${percentage.toFixed(0)}%`;
  brakeFillEl.style.width = `${percentage}%`;
  
  // Add data point to chart with absolute timestamp like the working example
  if (brakeTimeSeries) {
    brakeTimeSeries.append(Date.now(), percentage);
    console.log(`Brake chart data: ${Date.now()}, ${percentage}%`);
    
    // Debug TimeSeries state
    if (brakeTimeSeries.data.length > 0) {
      console.log(`Brake TimeSeries has ${brakeTimeSeries.data.length} data points`);
    }
  }
}

function updateThrottleDisplay(throttle) {
  // Convertir en pourcentage et limiter à 100%
  const percentage = Math.min(Math.max(throttle * 100, 0), 100);
  throttleValueEl.textContent = `${percentage.toFixed(0)}%`;
  throttleFillEl.style.width = `${percentage}%`;
  
  // Add data point to chart with absolute timestamp like the working example
  if (throttleTimeSeries) {
    throttleTimeSeries.append(Date.now(), percentage);
    console.log(`Throttle chart data: ${Date.now()}, ${percentage}%`);
    
    // Debug TimeSeries state
    if (throttleTimeSeries.data.length > 0) {
      console.log(`Throttle TimeSeries has ${throttleTimeSeries.data.length} data points`);
    }
  }
}

function updateSessionDisplay(session) {
  // Réinitialiser les classes CSS
  sessionValueEl.className = 'session-display';
  
  // Démarrer la collecte de données si on entre en qualifications
  if ((session >= 5 && session <= 8) && !isCollectingData) {
    startDataCollection();
  }
  
  // Mettre à jour la session courante
  currentSession = session;
  
  // Mapping des valeurs de session selon rF2data.py
  // 0=testday 1-4=practice 5-8=qual 9=warmup 10-13=race
  if (session === 0) {
    sessionValueEl.textContent = 'TEST';
    sessionValueEl.classList.add('testday');
    sessionDescriptionEl.textContent = 'Journée de test';
  } else if (session >= 1 && session <= 4) {
    sessionValueEl.textContent = 'P' + session;
    sessionValueEl.classList.add('practice');
    sessionDescriptionEl.textContent = `Essais libres ${session}`;
  } else if (session >= 5 && session <= 8) {
    const qualSession = session - 4;
    sessionValueEl.textContent = 'Q' + qualSession;
    sessionValueEl.classList.add('qualifying');
    sessionDescriptionEl.textContent = `Qualifications ${qualSession}`;
  } else if (session === 9) {
    sessionValueEl.textContent = 'WARM';
    sessionValueEl.classList.add('warmup');
    sessionDescriptionEl.textContent = 'Échauffement';
  } else if (session >= 10 && session <= 13) {
    const raceSession = session - 9;
    sessionValueEl.textContent = 'R' + raceSession;
    sessionValueEl.classList.add('race');
    sessionDescriptionEl.textContent = `Course ${raceSession}`;
    
    // Afficher le bouton d'export pendant la course
    updateExportButtonVisibility(true);
  } else {
    sessionValueEl.textContent = '?';
    sessionDescriptionEl.textContent = 'Session inconnue';
  }
  
  // Cacher le bouton d'export si on n'est pas en course
  if (session < 10 || session > 13) {
    updateExportButtonVisibility(false);
  }
}

function startDataCollection() {
  console.log('Démarrage de la collecte de données de télémétrie');
  isCollectingData = true;
  telemetryData = []; // Reset des données
}

function collectTelemetryData(data) {
  if (!isCollectingData) return;
  
  // Vérifier que toutes les données requises sont présentes
  if (typeof data.session !== 'number' ||
      typeof data.gear !== 'number' ||
      typeof data.brake !== 'number' ||
      typeof data.throttle !== 'number' ||
      !data.driverName ||
      !data.vehicleName ||
      typeof data.place !== 'number') {
    console.warn('Données incomplètes, point ignoré:', data);
    return;
  }
  
  const timestamp = new Date().toISOString();
  const dataPoint = {
    timestamp: timestamp,
    session: data.session,
    gear: data.gear,
    brake: data.brake,
    throttle: data.throttle,
    driverName: data.driverName,
    vehicleName: data.vehicleName,
    trackName: data.trackName || 'Unknown Track',
    place: data.place
  };
  
  telemetryData.push(dataPoint);
  console.log(`Données collectées: ${telemetryData.length} points`);
}

function updateExportButtonVisibility(visible) {
  const exportBtn = document.getElementById('exportBtn');
  if (exportBtn) {
    exportBtn.style.display = visible ? 'block' : 'none';
  }
}

function updateTrackDisplay(trackName) {
  if (trackName && trackName.trim()) {
    trackValueEl.textContent = trackName;
  } else {
    trackValueEl.textContent = 'Circuit inconnu';
  }
}

function updateVehicleDisplay(vehicleName) {
  if (vehicleName && vehicleName.trim()) {
    vehicleValueEl.textContent = vehicleName;
  } else {
    vehicleValueEl.textContent = 'Véhicule inconnu';
  }
}

function cleanTelemetryData() {
  // Nettoyer les données incomplètes avant l'export
  const cleanedData = telemetryData.filter(point => {
    return typeof point.session === 'number' &&
           typeof point.gear === 'number' &&
           typeof point.brake === 'number' &&
           typeof point.throttle === 'number' &&
           point.driverName &&
           point.vehicleName &&
           typeof point.place === 'number';
  });
  
  if (cleanedData.length !== telemetryData.length) {
    console.log(`Nettoyage: ${telemetryData.length - cleanedData.length} points incomplets supprimés`);
  }
  
  return cleanedData;
}

async function exportTelemetryData() {
  if (telemetryData.length === 0) {
    alert('Aucune donnée à exporter');
    return;
  }
  
  // Nettoyer les données avant l'export
  const cleanedData = cleanTelemetryData();
  
  if (cleanedData.length === 0) {
    alert('Aucune donnée complète à exporter');
    return;
  }
  
  const exportBtn = document.getElementById('exportBtn');
  const originalText = exportBtn.textContent;
  exportBtn.textContent = 'Export en cours...';
  exportBtn.disabled = true;
  
  try {
    const response = await fetch('http://localhost:8000/export-csv', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data: cleanedData,
        sessionInfo: {
          currentSession: currentSession,
          totalPoints: cleanedData.length,
          startTime: cleanedData[0]?.timestamp,
          endTime: cleanedData[cleanedData.length - 1]?.timestamp
        }
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      const message = `Export réussi ! 
Fichier: ${result.filename}
Points exportés: ${cleanedData.length}
${telemetryData.length !== cleanedData.length ? 
  `Points supprimés (incomplets): ${telemetryData.length - cleanedData.length}` : ''}`;
      alert(message);
    } else {
      const errorData = await response.json();
      console.error('Détails de l\'erreur:', errorData);
      throw new Error('Erreur lors de l\'export');
    }
  } catch (error) {
    console.error('Erreur export:', error);
    alert('Erreur lors de l\'export des données');
  } finally {
    exportBtn.textContent = originalText;
    exportBtn.disabled = false;
  }
}

function connectWebSocket() {
  sock = new WebSocket(WS_URL);

  sock.onopen = () => {
    statusEl.textContent = 'Connecté';
    statusEl.className = 'status connected';
    console.log('WebSocket connected');
  };

  sock.onmessage = (evt) => {
    let obj;
    try {
      obj = JSON.parse(evt.data);
    } catch (e) {
      console.warn("JSON invalide:", e);
      return;
    }
    
    // Mettre à jour les affichages
    if (typeof obj.gear === 'number') {
      updateGearDisplay(obj.gear);
    }
    if (typeof obj.brake === 'number') {
      updateBrakeDisplay(obj.brake);
    }
    if (typeof obj.throttle === 'number') {
      updateThrottleDisplay(obj.throttle);
    }
    if (typeof obj.session === 'number') {
      updateSessionDisplay(obj.session);
    }
    if (obj.trackName !== undefined) {
      updateTrackDisplay(obj.trackName);
    }
    if (obj.vehicleName !== undefined) {
      updateVehicleDisplay(obj.vehicleName);
    }
    
    // Collecter les données pour l'export
    collectTelemetryData(obj);
  };

  sock.onclose = (ev) => {
    statusEl.textContent = 'Déconnecté - Reconnexion...';
    statusEl.className = 'status disconnected';
    gearValueEl.textContent = '-';
    gearDescriptionEl.textContent = 'Connexion perdue';
    sessionValueEl.textContent = '-';
    sessionDescriptionEl.textContent = 'Connexion perdue';
    trackValueEl.textContent = '-';
    vehicleValueEl.textContent = '-';
    setTimeout(connectWebSocket, 1000);
  };

  sock.onerror = (err) => {
    console.error("Erreur WebSocket:", err);
    statusEl.textContent = 'Erreur de connexion';
    statusEl.className = 'status disconnected';
  };
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, initializing charts...');
  initializeCharts();
  connectWebSocket();
});
