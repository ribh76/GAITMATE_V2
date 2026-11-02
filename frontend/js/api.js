const API_BASE_URL = "http://127.0.0.1:5001/api";

async function apiGet(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `Request failed with ${response.status}`);
  }
  return data;
}

export function getHealth() {
  return apiGet("/health");
}

export function getLatestSensorData() {
  return apiGet("/sensor/latest");
}

export function getLatestLigamentData() {
  return apiGet("/sensor/ligaments/latest");
}

export function getLatestRisk() {
  return apiGet("/risk/latest");
}
