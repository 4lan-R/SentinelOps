const state = {
  metrics: null,
  incidents: [],
  monitoring: false,
  websocketConnected: false,
};

const elements = {
  cpuValue: document.getElementById('cpuValue'),
  memoryValue: document.getElementById('memoryValue'),
  apiErrorRate: document.getElementById('apiErrorRate'),
  dbLatency: document.getElementById('dbLatency'),
  monitoringStatus: document.getElementById('monitoringStatus'),
  lastRefresh: document.getElementById('lastRefresh'),
  wsStatus: document.getElementById('wsStatus'),
  incidentRows: document.getElementById('incidentRows'),
  alertFeed: document.getElementById('alertFeed'),
  startButton: document.getElementById('startMonitoring'),
  stopButton: document.getElementById('stopMonitoring'),
};

const api = {
  metrics: '/monitoring/metrics',
  status: '/monitoring/status',
  start: '/monitoring/start',
  stop: '/monitoring/stop',
  incidents: '/incidents',
};

function formatPercent(value) {
  return `${Math.round(value * 100) / 100}%`;
}

function createIncidentRow(incident) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${incident.id}</td>
    <td>${incident.title}</td>
    <td>${incident.service}</td>
    <td>${incident.severity}</td>
    <td>${incident.status}</td>
  `;
  return row;
}

function updateIncidentTable(incidents) {
  elements.incidentRows.innerHTML = '';
  if (!incidents.length) {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="5">No incidents reported.</td>';
    elements.incidentRows.appendChild(row);
    return;
  }

  incidents.slice(0, 8).forEach((incident) => {
    elements.incidentRows.appendChild(createIncidentRow(incident));
  });
}

function pushAlert(message) {
  const item = document.createElement('li');
  item.innerHTML = `<strong>${message.type || 'Alert'}</strong><span>${message.payload ? JSON.stringify(message.payload) : JSON.stringify(message)}</span>`;
  elements.alertFeed.prepend(item);
  while (elements.alertFeed.children.length > 10) {
    elements.alertFeed.removeChild(elements.alertFeed.lastChild);
  }
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function refreshMetrics() {
  const data = await fetchJson(api.metrics);
  state.metrics = data.metrics;
  const { cpu_usage, memory_usage, api_error_rate, db_latency_ms } = state.metrics;
  elements.cpuValue.textContent = formatPercent(cpu_usage);
  elements.memoryValue.textContent = formatPercent(memory_usage);
  elements.apiErrorRate.textContent = formatPercent(api_error_rate * 100);
  elements.dbLatency.textContent = `${db_latency_ms.toFixed(0)} ms`;
}

async function refreshMonitoringStatus() {
  const data = await fetchJson(api.status);
  state.monitoring = data.running;
  elements.monitoringStatus.textContent = state.monitoring ? 'Running' : 'Stopped';
  elements.monitoringStatus.style.color = state.monitoring ? '#7dd3fc' : '#f87171';
}

async function refreshIncidents() {
  const data = await fetchJson(api.incidents);
  state.incidents = data;
  updateIncidentTable(data);
}

async function refreshAll() {
  try {
    await Promise.all([refreshMetrics(), refreshMonitoringStatus(), refreshIncidents()]);
    elements.lastRefresh.textContent = new Date().toLocaleTimeString();
  } catch (error) {
    console.error('Refresh failed', error);
  }
}

async function sendControl(path) {
  try {
    const result = await fetchJson(path, { method: 'POST' });
    pushAlert({ type: 'System', payload: result });
    await refreshMonitoringStatus();
  } catch (error) {
    console.error('Control action failed', error);
  }
}

function initWebsocket() {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/alerts`);

  socket.addEventListener('open', () => {
    state.websocketConnected = true;
    elements.wsStatus.textContent = 'Connected';
    elements.wsStatus.style.color = '#86efac';
  });

  socket.addEventListener('message', (event) => {
    try {
      pushAlert(JSON.parse(event.data));
    } catch (error) {
      pushAlert({ type: 'message', payload: event.data });
    }
  });

  socket.addEventListener('close', () => {
    state.websocketConnected = false;
    elements.wsStatus.textContent = 'Disconnected';
    elements.wsStatus.style.color = '#f87171';
    setTimeout(initWebsocket, 3000);
  });

  socket.addEventListener('error', () => {
    state.websocketConnected = false;
    elements.wsStatus.textContent = 'Error';
    elements.wsStatus.style.color = '#f87171';
  });
}

elements.startButton.addEventListener('click', () => sendControl(api.start));
elements.stopButton.addEventListener('click', () => sendControl(api.stop));

refreshAll();
setInterval(refreshAll, 5000);
initWebsocket();
