
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interfaces
export const getInterfaces = async () => {
  const response = await api.get("/interfaces/");
  return response.data;
};

// Capture
export const startCapture = async (interfaceName) => {
  const response = await api.post("/capture/start", {
    interface: interfaceName,
  });
  return response.data;
};

export const stopCapture = async () => {
  const response = await api.post("/capture/stop");
  return response.data;
};

export const getCaptureStatus = async () => {
  const response = await api.get("/capture/status");
  return response.data;
};

export const getCapturedPackets = async (limit = 100) => {
  const response = await api.get("/capture/packets", {
    params: { limit },
  });
  return response.data;
};

// Analytics
export const getAnalytics = async (windowSeconds = 10, topLimit = 5) => {
  const response = await api.get("/analytics/", {
    params: {
      window_seconds: windowSeconds,
      top_limit: topLimit,
    },
  });
  return response.data;
};

// Traffic History
export const getTrafficHistory = async (limit = 60) => {
  const response = await api.get("/history/", {
    params: { limit },
  });
  return response.data;
};

// Anomaly Detection
export const getAnomalyStatus = async () => {
  const response = await api.get("/anomalies/status");
  return response.data;
};

export const getAnomalyAlerts = async (limit = 50) => {
  const response = await api.get("/anomalies/alerts", {
    params: { limit },
  });
  return response.data;
};

export const analyzeAnomalies = async () => {
  const response = await api.post("/anomalies/analyze");
  return response.data;
};

export default api;
