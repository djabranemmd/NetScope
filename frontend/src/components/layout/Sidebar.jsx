
import {
  Activity,
  LayoutDashboard,
  Network,
  ShieldAlert,
  Radio,
  Settings,
  CircleHelp,
} from "lucide-react";

const navigation = [
  {
    label: "Overview",
    icon: LayoutDashboard,
    href: "#overview",
    active: true,
  },
  {
    label: "Traffic Analytics",
    icon: Activity,
    href: "#analytics",
  },
  {
    label: "Network Interfaces",
    icon: Network,
    href: "#interfaces",
  },
  {
    label: "Anomaly Detection",
    icon: ShieldAlert,
    href: "#anomalies",
  },
  {
    label: "Packet Capture",
    icon: Radio,
    href: "#capture",
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Activity size={23} />
        </div>

        <div className="brand-text">
          <h1>NetScope</h1>
          <span>NETWORK INTELLIGENCE</span>
        </div>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-section-label">MAIN MENU</span>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <a
                key={item.label}
                href={item.href}
                className={`nav-item ${item.active ? "active" : ""}`}
              >
                <Icon size={19} strokeWidth={1.8} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </div>

      <div className="sidebar-bottom">
        <a href="#settings" className="nav-item">
          <Settings size={19} />
          <span>Settings</span>
        </a>

        <a href="#help" className="nav-item">
          <CircleHelp size={19} />
          <span>Documentation</span>
        </a>

        <div className="sidebar-version">
          <span className="version-dot" />
          <span>NetScope v0.5.0</span>
        </div>
      </div>
    </aside>
  );
}
