import React from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, AreaChart, Area 
} from 'recharts';
import { BarChart3, PieChart as PieIcon, TrendingUp, ShieldCheck, AlertOctagon } from 'lucide-react';

export default function AnalyticsView({ stats, loading }) {
  const riskData = stats?.risk_distribution || [
    { name: 'High Risk (75-100)', value: 0, color: '#ef4444' },
    { name: 'Suspicious (50-74)', value: 0, color: '#f97316' },
    { name: 'Caution (25-49)', value: 0, color: '#eab308' },
    { name: 'Likely Safe (0-24)', value: 0, color: '#10b981' }
  ];

  const categoryData = stats?.category_breakdown || [];
  const timelineData = stats?.timeline || [];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="cyber-card p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-emerald-400" />
            Threat Intelligence & Risk Distribution Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry gathered across WhatsApp inbound webhooks and the interactive testing sandbox.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            Threat Neutralization: <strong className="text-emerald-400 font-mono">{stats?.threat_neutralized_rate || 0}%</strong>
          </div>
        </div>
      </div>

      {/* Row 1: Donut & Category Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Level Distribution Donut */}
        <div className="cyber-card p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-cyan-400" />
              Risk Severity Band Distribution
            </h3>
            <span className="text-xs font-mono text-slate-400">Total Scans: {stats?.total_scans || 0}</span>
          </div>

          <div className="h-64 my-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800/60 text-center">
            {riskData.map((item, idx) => (
              <div key={idx} className="p-2 rounded-lg bg-slate-950/50">
                <span className="text-[10px] text-slate-400 block truncate">{item.name.split(' ')[0]}</span>
                <span className="text-base font-bold font-mono" style={{ color: item.color }}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Categories Bar Chart */}
        <div className="cyber-card p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-orange-400" />
              Threat Categories Incident Frequency
            </h3>
            <span className="text-xs font-mono text-slate-400">Top Detected Patterns</span>
          </div>

          <div className="h-64 my-4">
            {categoryData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis 
                    dataKey="category" 
                    stroke="#64748b" 
                    fontSize={10} 
                    angle={-25} 
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                No threat categories logged yet. Run a scan from the Live Scanner.
              </div>
            )}
          </div>

          <p className="text-[11px] text-slate-500 pt-2 border-t border-slate-800/60">
            Breakdown based on KYC alerts, lottery claims, task recruitment fraud, and viral hoaxes.
          </p>
        </div>
      </div>

      {/* Row 2: Chronological Threat Score Progression */}
      <div className="cyber-card p-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            Recent Temporal Threat Volumetrics & Score Trend
          </h3>
          <span className="text-xs text-slate-400">Recent 20 audit events</span>
        </div>

        <div className="h-60 mt-4">
          {timelineData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="risk_score" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#riskGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-500">
              No historical data available yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
