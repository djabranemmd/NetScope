
import { Bell, RefreshCw } from "lucide-react";

export default function Topbar({
  apiConnected,
  lastUpdated,
  loading,
  onRefresh,
}) {
  const formattedTime = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString()
    : "Not updated yet";

  return (
    <header className="topbar">
      <div className="topbar-heading">
        <span className="breadcrumb">NetScope /</span>
        <h2>Network Overview</h2>
      </div>

      <div className="topbar-actions">
        <div className="api-status">
          <span
            className={`status-dot ${
              apiConnected ? "online" : "offline"
            }`}
          />
          <span>
            {apiConnected ? "API Connected" : "API Unavailable"}
          </span>
        </div>

        <button
          className="icon-button"
          type="button"
          aria-label="Refresh data"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh data"
        >
          <RefreshCw
            size={18}
            className={loading ? "spin" : ""}
          />
        </button>

        <button
          className="icon-button"
          type="button"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell size={18} />
        </button>

        <div className="topbar-divider" />

        <div className="last-updated">
          <span>LAST UPDATED</span>
          <strong>{formattedTime}</strong>
        </div>
      </div>
    </header>
  );
}
