
import { useCallback, useEffect, useState } from "react";
import {
  ShieldCheck, Activity, AlertTriangle, CheckCircle,
  Search, RefreshCw, ShieldAlert, Clock3, X, Server
} from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend
} from "recharts";
import "./App.css";

const API = "http://127.0.0.1:5000";
const API_KEY = "dev-secret-change-me";

const COLORS = {
  Benign: "#22c55e",
  Suspicious: "#f59e0b",
  Malicious: "#ef4444",
};

function App() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    total_events: 0,
    risk_counts: { Benign: 0, Suspicious: 0, Malicious: 0 },
    status_counts: { New: 0, "In Progress": 0, Resolved: 0 },
  });
  const [riskFilter, setRiskFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      if (riskFilter) params.set("risk_level", riskFilter);
      if (statusFilter) params.set("status", statusFilter);

      const [eventResponse, statsResponse] = await Promise.all([
        fetch(`${API}/events?${params.toString()}`),
        fetch(`${API}/stats`),
      ]);

      if (!eventResponse.ok || !statsResponse.ok) {
        throw new Error("Could not load dashboard data.");
      }

      const eventData = await eventResponse.json();
      const statsData = await statsResponse.json();

      setEvents(eventData.events || []);
      setStats(statsData);
    } catch {
      setError(
        "Cannot connect to the backend. Check that Flask is running on port 5000."
      );
    } finally {
      setLoading(false);
    }
  }, [riskFilter, statusFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updateStatus = async (eventId, status) => {
    setError("");
    setNotice("");

    try {
      const response = await fetch(`${API}/events/${eventId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ status }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Could not update status.");
      }

      setSelectedEvent(result);
      setNotice(`Event #${eventId} updated to ${status}.`);
      await loadData();
    } catch (err) {
      setError(err.message || "Could not update event.");
    }
  };

  const visibleEvents = events.filter((event) => {
    const term = search.toLowerCase();
    return (
      (event.raw_log || "").toLowerCase().includes(term) ||
      (event.source || "").toLowerCase().includes(term) ||
      String(event.id).includes(term)
    );
  });

  const riskData = ["Benign", "Suspicious", "Malicious"].map((name) => ({
    name,
    value: stats.risk_counts?.[name] || 0,
  }));

  const formatDate = (date) => {
    if (!date) return "—";
    return new Date(date).toLocaleString();
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={27} /></div>
          <div>
            <h2>RAKSHA<span>SOC</span></h2>
            <p>SECURITY OPERATIONS</p>
          </div>
        </div>

        <div className="side-label">WORKSPACE</div>
        <div className="nav-item active">
          <Activity size={18} /> Security Overview
        </div>
        <div className="nav-item">
          <ShieldAlert size={18} /> Security Events
        </div>

        <div className="sidebar-bottom">
          <div className="connection-dot" />
          <div>
            <strong>Backend API</strong>
            <p>127.0.0.1:5000</p>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">SECURITY CENTER / OVERVIEW</p>
            <h1>Security Dashboard</h1>
            <p className="subheading">
              Monitor, investigate, and manage security events.
            </p>
          </div>
          <button className="refresh-button" onClick={loadData} disabled={loading}>
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            {loading ? "Loading..." : "Refresh"}
          </button>
        </header>

        {error && <div className="message error-message">{error}</div>}
        {notice && <div className="message success-message">{notice}</div>}

        <section className="stat-grid">
          <StatCard
            icon={<Server />}
            label="Total Events"
            value={stats.total_events || 0}
            color="blue"
          />
          <StatCard
            icon={<ShieldAlert />}
            label="Malicious"
            value={stats.risk_counts?.Malicious || 0}
            color="red"
          />
          <StatCard
            icon={<AlertTriangle />}
            label="Suspicious"
            value={stats.risk_counts?.Suspicious || 0}
            color="amber"
          />
          <StatCard
            icon={<CheckCircle />}
            label="Benign"
            value={stats.risk_counts?.Benign || 0}
            color="green"
          />
        </section>

        <section className="content-grid">
          <div className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <h3>Risk Distribution</h3>
                <p>Events grouped by ML-predicted risk level</p>
              </div>
              <Activity size={19} />
            </div>

            {riskData.reduce((sum, item) => sum + item.value, 0) === 0 ? (
              <div className="empty-chart">
                <Activity size={30} />
                <p>No events to display yet</p>
              </div>
            ) : (
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="46%"
                      innerRadius={65}
                      outerRadius={100}
                      paddingAngle={4}
                    >
                      {riskData.map((entry) => (
                        <Cell key={entry.name} fill={COLORS[entry.name]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend verticalAlign="bottom" />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="panel status-panel">
            <div className="panel-heading">
              <div>
                <h3>Case Status</h3>
                <p>Current incident workflow</p>
              </div>
              <Clock3 size={19} />
            </div>

            {["New", "In Progress", "Resolved"].map((status) => (
              <div className="status-row" key={status}>
                <div className="status-name">
                  <span className={`status-dot ${status.replace(" ", "-").toLowerCase()}`} />
                  {status}
                </div>
                <strong>{stats.status_counts?.[status] || 0}</strong>
              </div>
            ))}

            <div className="status-note">
              <ShieldCheck size={18} />
              <span>Keep event statuses updated during investigation.</span>
            </div>
          </div>
        </section>

        <section className="panel events-panel">
          <div className="events-heading">
            <div>
              <h3>Security Events</h3>
              <p>Review and manage detected security logs.</p>
            </div>
            <span className="event-count">{visibleEvents.length} events</span>
          </div>

          <div className="filters">
            <div className="search-box">
              <Search size={17} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search log, source, or ID..."
              />
            </div>

            <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
              <option value="">All risk levels</option>
              <option value="Benign">Benign</option>
              <option value="Suspicious">Suspicious</option>
              <option value="Malicious">Malicious</option>
            </select>

            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All statuses</option>
              <option value="New">New</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Security Log</th>
                  <th>Source</th>
                  <th>Risk Level</th>
                  <th>Confidence</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {visibleEvents.map((event) => (
                  <tr key={event.id}>
                    <td className="id-cell">#{event.id}</td>
                    <td className="log-cell">{event.raw_log}</td>
                    <td>{event.source}</td>
                    <td>
                      <span className={`risk-badge ${event.risk_level?.toLowerCase()}`}>
                        {event.risk_level}
                      </span>
                    </td>
                    <td>{(Number(event.confidence) * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`status-badge ${event.status.replace(" ", "-").toLowerCase()}`}>
                        {event.status}
                      </span>
                    </td>
                    <td className="date-cell">{formatDate(event.timestamp)}</td>
                    <td>
                      <button className="details-button" onClick={() => setSelectedEvent(event)}>
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {!loading && visibleEvents.length === 0 && (
              <div className="empty-table">
                <Search size={25} />
                <p>No matching events found.</p>
                <span>Try changing your filters or add a security event.</span>
              </div>
            )}
          </div>
        </section>

        <footer className="footer">
          <span><ShieldCheck size={15} /> Raksha SOC</span>
          <span>ML-assisted security monitoring · Demo environment</span>
        </footer>
      </main>

      {selectedEvent && (
        <div className="modal-backdrop" onClick={() => setSelectedEvent(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-heading">
              <div>
                <p className="eyebrow">EVENT DETAILS</p>
                <h2>Security Event #{selectedEvent.id}</h2>
              </div>
              <button className="close-button" onClick={() => setSelectedEvent(null)}>
                <X size={20} />
              </button>
            </div>

            <div className="detail-field">
              <label>Raw Security Log</label>
              <p className="raw-log">{selectedEvent.raw_log}</p>
            </div>

            <div className="detail-two-col">
              <div className="detail-field">
                <label>Source</label>
                <p>{selectedEvent.source}</p>
              </div>
              <div className="detail-field">
                <label>Predicted Risk</label>
                <p>
                  <span className={`risk-badge ${selectedEvent.risk_level?.toLowerCase()}`}>
                    {selectedEvent.risk_level}
                  </span>
                </p>
              </div>
              <div className="detail-field">
                <label>Model Confidence</label>
                <p>{(Number(selectedEvent.confidence) * 100).toFixed(1)}%</p>
              </div>
              <div className="detail-field">
                <label>Timestamp</label>
                <p>{formatDate(selectedEvent.timestamp)}</p>
              </div>
            </div>

            <div className="detail-field">
              <label>Update Case Status</label>
              <select
                value={selectedEvent.status}
                onChange={(e) => updateStatus(selectedEvent.id, e.target.value)}
              >
                <option value="New">New</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>

            <p className="modal-footnote">
              ML confidence is a model estimate, not a guarantee of threat severity.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${color}`}>{icon}</div>
      <div>
        <p>{label}</p>
        <h2>{value}</h2>
      </div>
      <div className={`stat-accent ${color}`} />
    </div>
  );
}

export default App;
