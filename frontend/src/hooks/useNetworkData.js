
import { useCallback, useEffect, useState } from "react";

import {
  getInterfaces,
  getCaptureStatus,
  getAnalytics,
  getTrafficHistory,
  getAnomalyStatus,
  getAnomalyAlerts,
} from "../services/api";

const POLLING_INTERVAL = 3000;

const initialData = {
  interfaces: null,
  captureStatus: null,
  analytics: null,
  history: null,
  anomalyStatus: null,
  alerts: null,
};

export default function useNetworkData() {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const refreshData = useCallback(async () => {
    const requests = [
      getInterfaces(),
      getCaptureStatus(),
      getAnalytics(),
      getTrafficHistory(),
      getAnomalyStatus(),
      getAnomalyAlerts(),
    ];

    const results = await Promise.allSettled(requests);

    const keys = [
      "interfaces",
      "captureStatus",
      "analytics",
      "history",
      "anomalyStatus",
      "alerts",
    ];

    const failedRequests = [];

    setData((previousData) => {
      const updatedData = { ...previousData };

      results.forEach((result, index) => {
        if (result.status === "fulfilled") {
          updatedData[keys[index]] = result.value;
        } else {
          failedRequests.push(keys[index]);
        }
      });

      return updatedData;
    });

    if (failedRequests.length > 0) {
      setError(
        `Failed to retrieve: ${failedRequests.join(", ")}`
      );
    } else {
      setError(null);
    }

    setLastUpdated(new Date().toISOString());
    setLoading(false);
  }, []);

  useEffect(() => {
    refreshData();

    const intervalId = setInterval(() => {
      refreshData();
    }, POLLING_INTERVAL);

    return () => {
      clearInterval(intervalId);
    };
  }, [refreshData]);

  return {
    ...data,
    loading,
    error,
    lastUpdated,
    refreshData,
  };
}
