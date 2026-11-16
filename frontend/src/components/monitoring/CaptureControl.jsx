
import { useState } from "react";
import { Play, Square, Radio, LoaderCircle } from "lucide-react";

import {
  startCapture,
  stopCapture,
} from "../../services/api";

import "./CaptureControl.css";

export default function CaptureControl({
  interfaces,
  captureStatus,
  onCaptureChange,
}) {
  const availableInterfaces = (interfaces?.interfaces || []).filter(
    (item) => item.has_ipv4
  );

  const defaultInterface = interfaces?.default_interface || "";

  const [selectedInterface, setSelectedInterface] = useState(
    defaultInterface
  );
  const [isBusy, setIsBusy] = useState(false);
  const [operationError, setOperationError] = useState(null);

  const isRunning = captureStatus?.capture?.is_running === true;
  const activeInterface = captureStatus?.capture?.interface;

  const handleStart = async () => {
    if (!selectedInterface) {
      setOperationError("Please select a network interface.");
      return;
    }

    setIsBusy(true);
    setOperationError(null);

    try {
      await startCapture(selectedInterface);
      await onCaptureChange();
    } catch (error) {
      setOperationError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to start packet capture."
      );
    } finally {
      setIsBusy(false);
    }
  };

  const handleStop = async () => {
    setIsBusy(true);
    setOperationError(null);

    try {
      await stopCapture();
      await onCaptureChange();
    } catch (error) {
      setOperationError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to stop packet capture."
      );
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <section className="capture-control">
      <div className="capture-control-header">
        <div className="capture-control-title">
          <div className="capture-control-icon">
            <Radio size={20} />
          </div>

          <div>
            <h3>Packet Capture Control</h3>
            <p>Manage real-time network packet collection</p>
          </div>
        </div>

        <div
          className={`capture-state ${
            isRunning ? "capture-active" : "capture-inactive"
          }`}
        >
          <span className="status-dot" />
          {isRunning ? "CAPTURING" : "STOPPED"}
        </div>
      </div>

      <div className="capture-control-body">
        <div className="interface-selector">
          <label htmlFor="network-interface">NETWORK INTERFACE</label>

          <select
            id="network-interface"
            value={selectedInterface}
            onChange={(event) => setSelectedInterface(event.target.value)}
            disabled={isRunning || isBusy}
          >
            <option value="">Select an interface</option>

            {availableInterfaces.map((item) => (
              <option key={item.name} value={item.name}>
                {item.name} — {item.ip_address}
                {item.is_default_route ? " (Default)" : ""}
              </option>
            ))}
          </select>

          <span className="interface-hint">
            {availableInterfaces.length} IPv4-enabled interface(s) available
          </span>
        </div>

        <div className="capture-actions">
          {!isRunning ? (
            <button
              type="button"
              className="capture-start-button"
              onClick={handleStart}
              disabled={isBusy || !selectedInterface}
            >
              {isBusy ? (
                <LoaderCircle className="spin" size={17} />
              ) : (
                <Play size={17} />
              )}
              Start Capture
            </button>
          ) : (
            <button
              type="button"
              className="capture-stop-button"
              onClick={handleStop}
              disabled={isBusy}
            >
              {isBusy ? (
                <LoaderCircle className="spin" size={17} />
              ) : (
                <Square size={16} />
              )}
              Stop Capture
            </button>
          )}
        </div>
      </div>

      {isRunning && (
        <div className="capture-running-info">
          <span className="status-dot online" />
          <span>
            Capturing on <strong>{activeInterface}</strong>
          </span>
        </div>
      )}

      {operationError && (
        <div className="capture-error">{operationError}</div>
      )}
    </section>
  );
}
