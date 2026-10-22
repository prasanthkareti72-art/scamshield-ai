import React from 'react';
import { ShieldAlert, ShieldCheck, Activity, AlertOctagon, CheckCircle2 } from 'lucide-react';

export default function StatCards({ stats, loading }) {
  const cards = [
    {
      title: 'Total Scans Logged',
      value: stats?.total_scans ?? 0,
      icon: Activity,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
      border: 'border-cyan-500/20',
      detail: 'WhatsApp & Dashboard',
    },
    {
      title: 'High-Risk Threats Blocked',
      value: stats?.high_risk_count ?? 0,
      icon: ShieldAlert,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/20',
      detail: 'Score 75 - 100 range',
    },
    {
      title: 'Suspicious & Caution',
      value: (stats?.suspicious_count ?? 0) + (stats?.caution_count ?? 0),
      icon: AlertOctagon,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      detail: 'Under verification',
    },
    {
      title: 'Likely Safe Messages',
      value: stats?.safe_count ?? 0,
      icon: ShieldCheck,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      detail: 'Benign communications',
    },
    {
      title: 'Avg Threat Risk Score',
      value: `${stats?.average_risk_score ?? 0}/100`,
      icon: CheckCircle2,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/20',
      detail: 'Normalized 0-100 metric',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div key={i} className="cyber-card p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-400 tracking-wider">
                {c.title}
              </span>
              <div className={`p-2 rounded-lg ${c.bg} ${c.border} border`}>
                <Icon className={`w-4 h-4 ${c.color}`} />
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold tracking-tight text-white font-mono">
                {loading ? <span className="animate-pulse">--</span> : c.value}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">{c.detail}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
