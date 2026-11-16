
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./TrafficChart.css";

const PROTOCOL_COLORS = ["#38bdf8", "#a78bfa", "#34d399", "#f59e0b", "#f87171"];

const formatMbps = (value) => `${Number(value).toFixed(3)} Mbps`;

function TrafficChart({ history, analytics }) {
  const samples = history?.samples || [];
  const protocols = analytics?.data?.protocols || [];

  const chartData = samples.map((sample) => ({
    time: new Date(sample.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
    total: sample.bandwidth?.total_mbps ?? 0,
    incoming: sample.bandwidth?.incoming_mbps ?? 0,
    outgoing: sample.bandwidth?.outgoing_mbps ?? 0,
  }));

  const hasTrafficData = chartData.length > 0;
  const hasProtocolData = protocols.length > 0;

  return (
    <section className="traffic-analytics">
      <div className="traffic-chart-card">
        <div className="traffic-card-header">
          <div>
            <h3>Network Bandwidth</h3>
            <p>Real-time incoming and outgoing traffic</p>
          </div>
          <span className="chart-live-indicator">
            <span className="status-dot online" />
            LIVE DATA
          </span>
        </div>

        <div className="traffic-chart-container">
          {hasTrafficData ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{ top: 10, right: 12, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="totalGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>

                  <linearGradient id="incomingGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>

                  <linearGradient id="outgoingGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#a78bfa" stopOpacity={0} />
                  </linearGradient>
                </defs>

                <CartesianGrid stroke="#253247" strokeDasharray="3 3" />

                <XAxis
                  dataKey="time"
                  stroke="#718096"
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  minTickGap={30}
                />

                <YAxis
                  stroke="#718096"
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => value.toFixed(2)}
                  width={55}
                />

                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111a29",
                    border: "1px solid #253247",
                    borderRadius: "8px",
                    color: "#e2e8f0",
                  }}
                  labelStyle={{ color: "#94a3b8", marginBottom: 6 }}
                  formatter={(value, name) => [
                    formatMbps(value),
                    name,
                  ]}
                />

                <Legend
                  wrapperStyle={{
                    fontSize: "12px",
                    color: "#94a3b8",
                    paddingTop: "12px",
                  }}
                />

                <Area
                  type="monotone"
                  dataKey="total"
                  name="Total"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  fill="url(#totalGradient)"
                  dot={false}
                  activeDot={{ r: 4 }}
                />

                <Area
                  type="monotone"
                  dataKey="incoming"
                  name="Incoming"
                  stroke="#34d399"
                  strokeWidth={2}
                  fill="url(#incomingGradient)"
                  dot={false}
                  activeDot={{ r: 4 }}
                />

                <Area
                  type="monotone"
                  dataKey="outgoing"
                  name="Outgoing"
                  stroke="#a78bfa"
                  strokeWidth={2}
                  fill="url(#outgoingGradient)"
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty-state">
              <p>No traffic history available.</p>
              <span>Start packet capture to collect network data.</span>
            </div>
          )}
        </div>
      </div>

      <div className="traffic-chart-card protocol-card">
        <div className="traffic-card-header">
          <div>
            <h3>Protocol Distribution</h3>
            <p>Captured packets by protocol</p>
          </div>
        </div>

        <div className="protocol-chart-container">
          {hasProtocolData ? (
            <>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={protocols}
                    dataKey="packets"
                    nameKey="protocol"
                    cx="50%"
                    cy="50%"
                    innerRadius={58}
                    outerRadius={88}
                    paddingAngle={3}
                    stroke="none"
                  >
                    {protocols.map((protocol, index) => (
                      <Cell
                        key={protocol.protocol}
                        fill={PROTOCOL_COLORS[index % PROTOCOL_COLORS.length]}
                      />
                    ))}
                  </Pie>

                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#111a29",
                      border: "1px solid #253247",
                      borderRadius: "8px",
                      color: "#e2e8f0",
                    }}
                    formatter={(value, name) => [
                      `${value} packets`,
                      name,
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>

              <div className="protocol-legend">
                {protocols.map((protocol, index) => (
                  <div className="protocol-legend-item" key={protocol.protocol}>
                    <span
                      className="protocol-color"
                      style={{
                        backgroundColor:
                          PROTOCOL_COLORS[index % PROTOCOL_COLORS.length],
                      }}
                    />
                    <span className="protocol-name">{protocol.protocol}</span>
                    <strong>{protocol.packets.toLocaleString()}</strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="chart-empty-state">
              <p>No protocol data available.</p>
              <span>Start packet capture to analyze protocols.</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default TrafficChart;
