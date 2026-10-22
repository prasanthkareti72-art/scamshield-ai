/**
 * ScamShield AI - Frontend API Service Client
 */

const API_BASE = '/api';

export async function analyzeContent(message, source = 'web_dashboard') {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, source }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Analysis failed (${response.status})`);
  }
  return response.json();
}

export async function simulateWhatsApp(message, senderPhone = '+919876543210') {
  const response = await fetch(`${API_BASE}/webhook/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, sender_phone: senderPhone }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Simulation failed (${response.status})`);
  }
  return response.json();
}

export async function getStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) {
    throw new Error(`Failed to load stats (${response.status})`);
  }
  return response.json();
}

export async function getHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_BASE}/history?${query}`);
  if (!response.ok) {
    throw new Error(`Failed to load history (${response.status})`);
  }
  return response.json();
}

export async function getRulesAndMetrics() {
  const response = await fetch(`${API_BASE}/rules`);
  if (!response.ok) {
    throw new Error(`Failed to load rules & metrics (${response.status})`);
  }
  return response.json();
}

export async function clearAuditHistory() {
  const response = await fetch(`${API_BASE}/history/clear`, {
    method: 'POST',
  });
  return response.json();
}
