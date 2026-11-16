
import Sidebar from "./components/layout/Sidebar";
import Topbar from "./components/layout/Topbar";
import CaptureControl from "./components/monitoring/CaptureControl";
import TrafficChart from "./components/dashboard/TrafficChart";

import useNetworkData from "./hooks/useNetworkData";

import {
  Radio,
  ShieldCheck,
  Database,
  Server,
  Wifi,
} from "lucide-react";

function StatusCard({ title, value, description, icon: Icon, status }) {
  return (
    <div className="status-card">
      <div className="status-card-top">
        <div className="status-card-icon">
          <Icon size={21} />
        </div>

        <span className={`status-label ${status}`}>
          <span className="status-dot" />
          {value}
        </span>
      </div>

      <div className="status-card-content">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

function DashboardContent({
  interfaces,
  captureStatus,
  anomalyStatus,
  history,
  analytics,
  loading,
  error,
  onRefresh,
}) {
  const captureRunning =
    captureStatus?.capture?.is_running === true;

  const historyRunning =
    captureStatus?.history?.is_running === true;

  const anomalyRunning =
    anomalyStatus?.is_running === true ||
    captureStatus?.anomaly_detection?.is_running === true;

  const captureValue = captureStatus
    ? captureRunning
      ? "Running"
      : "Stopped"
    : "Unavailable";

  const historyValue = captureStatus
    ? historyRunning
      ? "Running"
      : "Stopped"
    : "Unavailable";

  const anomalyValue = anomalyStatus || captureStatus
    ? anomalyRunning
      ? "Active"
      : "Inactive"
    : "Unavailable";

  return (
    <main className="dashboard-content">
      <section className="page-heading">
        <div>
          <div className="page-eyebrow">
            <span className="eyebrow-line" />
            NETWORK MONITORING CENTER
          </div>

          <h1>Network Overview</h1>

          <p>
            Monitor your network traffic, analyze performance,
            and detect unusual activity in real time.
          </p>
        </div>

        <div className="environment-badge">
          <span className="status-dot online" />
          LOCAL ENVIRONMENT
        </div>
      </section>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
        </div>
      )}

      <section className="section-heading">
        <div>
          <h2>System Overview</h2>
          <p>Current status of your monitoring services</p>
        </div>
      </section>

      <section className="status-grid">
        <StatusCard
          title="Packet Capture"
          value={captureValue}
          description="Network packet collection engine"
          icon={Radio}
          status={captureRunning ? "success" : "neutral"}
        />

        <StatusCard
          title="Traffic History"
          value={historyValue}
          description="Traffic metrics collection service"
          icon={Database}
          status={historyRunning ? "success" : "neutral"}
        />

        <StatusCard
          title="Anomaly Detection"
          value={anomalyValue}
          description="Network traffic anomaly monitoring"
          icon={ShieldCheck}
          status={anomalyRunning ? "success" : "neutral"}
        />

        <StatusCard
          title="Backend API"
          value={captureStatus ? "Connected" : "Unavailable"}
          description="FastAPI communication status"
          icon={Server}
          status={captureStatus ? "success" : "neutral"}
        />
      </section>

      <section className="monitoring-section">
        <CaptureControl
          interfaces={interfaces}
          captureStatus={captureStatus}
          onCaptureChange={onRefresh}
        />
      </section>

      <section className="section-heading monitoring-heading">
        <div>
          <h2>Monitoring Workspace</h2>
          <p>Live network monitoring and analysis</p>
        </div>
      </section>

      <TrafficChart
        history={history}
        analytics={analytics}
      />

      <section className="workspace-grid">
        <div className="workspace-card">
          <div className="workspace-card-header">
            <div className="workspace-title">
              <Wifi size={19} />
              <h3>Network Activity</h3>
            </div>
          </div>

          <div className="empty-state">
            <Wifi size={32} />
            <h4>Network monitoring</h4>
            <p>
              Interface information and network activity
              will be displayed here.
            </p>
          </div>
        </div>
      </section>

      <div className="dashboard-footer">
        <span>
          <span className="footer-dot" />
          NetScope monitoring platform
        </span>
        <span>Data source: Local FastAPI backend</span>
      </div>

      {loading && !captureStatus && (
        <div className="loading-overlay">
          Connecting to monitoring services...
        </div>
      )}
    </main>
  );
}

export default function App() {
  const {
    interfaces,
    captureStatus,
    anomalyStatus,
    history,
    analytics,
    loading,
    error,
    lastUpdated,
    refreshData,
  } = useNetworkData();

  const apiConnected = Boolean(captureStatus);

  return (
    <div className="app-shell">
      <Sidebar />

      <div className="main-panel">
        <Topbar
          apiConnected={apiConnected}
          lastUpdated={lastUpdated}
          loading={loading}
          onRefresh={refreshData}
        />

        <DashboardContent
          interfaces={interfaces}
          captureStatus={captureStatus}
          anomalyStatus={anomalyStatus}
          history={history}
          analytics={analytics}
          loading={loading}
          error={error}
          onRefresh={refreshData}
        />
      </div>
    </div>
  );
}
