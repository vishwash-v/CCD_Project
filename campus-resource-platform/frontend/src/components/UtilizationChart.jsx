import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';

const COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export function PeakHoursChart({ data }) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([hour, count]) => ({
    hour: `${hour}:00`,
    bookings: count,
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">Peak Booking Hours</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="hour"
            stroke="#94a3b8"
            tick={{ fontSize: 11 }}
            interval={1}
          />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
          />
          <Bar
            dataKey="bookings"
            fill="url(#barGradient)"
            radius={[6, 6, 0, 0]}
          />
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#818cf8" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CategoryPieChart({ data }) {
  if (!data) return null;

  const chartData = Object.entries(data).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">Resources by Category</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
          />
          <Legend
            formatter={(value) => <span style={{ color: '#e2e8f0' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function UtilizationChart({ data }) {
  if (!data) return null;

  const chartData = Object.values(data).map((r) => ({
    name: r.name.length > 15 ? r.name.substring(0, 15) + '...' : r.name,
    utilization: r.utilization_percent,
    bookings: r.total_bookings,
  }));

  return (
    <div className="chart-container">
      <h3 className="chart-title">Resource Utilization (%)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" />
          <YAxis
            dataKey="name"
            type="category"
            width={120}
            stroke="#94a3b8"
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
          />
          <Bar dataKey="utilization" fill="url(#utilizationGradient)" radius={[0, 6, 6, 0]} />
          <defs>
            <linearGradient id="utilizationGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
