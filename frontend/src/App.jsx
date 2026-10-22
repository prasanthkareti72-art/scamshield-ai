import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import StatCards from './components/StatCards';
import LiveScanner from './components/LiveScanner';
import WhatsAppSimulator from './components/WhatsAppSimulator';
import AnalyticsView from './components/AnalyticsView';
import RecentScansTable from './components/RecentScansTable';
import ModelMetricsView from './components/ModelMetricsView';
import TwilioGuideView from './components/TwilioGuideView';
import { getStats } from './utils/api';
import { Shield } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('scanner');
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (e) {
      console.warn('Backend offline or initializing:', e);
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={stats}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Real-time Telemetry Stat Cards */}
        <StatCards stats={stats} loading={statsLoading} />

        {/* Tab View Content */}
        {activeTab === 'scanner' && (
          <LiveScanner onScanCompleted={fetchStats} />
        )}
        {activeTab === 'whatsapp' && (
          <WhatsAppSimulator onScanCompleted={fetchStats} />
        )}
        {activeTab === 'analytics' && (
          <AnalyticsView stats={stats} loading={statsLoading} />
        )}
        {activeTab === 'history' && (
          <RecentScansTable onScanCompleted={fetchStats} />
        )}
        {activeTab === 'rules' && (
          <ModelMetricsView />
        )}
        {activeTab === 'twilio' && (
          <TwilioGuideView />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-slate-400">ScamShield AI Platform</span>
            <span>—</span>
            <span>Centralized Fake News & Scam Detection Engine</span>
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-slate-500">
            <span>Flask REST Blueprints</span>
            <span>•</span>
            <span>scikit-learn NLP Pipeline</span>
            <span>•</span>
            <span>Twilio WhatsApp Webhooks</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
