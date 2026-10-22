import React from 'react';
import { Shield, MessageSquare, BarChart3, History, Cpu, BookOpen, AlertTriangle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, systemStatus }) {
  const tabs = [
    { id: 'scanner', label: 'Live Scanner', icon: Shield },
    { id: 'whatsapp', label: 'WhatsApp Simulator', icon: MessageSquare },
    { id: 'analytics', label: 'Threat Analytics', icon: BarChart3 },
    { id: 'history', label: 'Scan Audit Log', icon: History },
    { id: 'rules', label: 'AI & Detection Rules', icon: Cpu },
    { id: 'twilio', label: 'WhatsApp Setup', icon: BookOpen },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Shield className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                  ScamShield <span className="text-emerald-400">AI</span>
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  v1.0 Ready
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                WhatsApp Scam & Fake News Detection Engine
              </p>
            </div>
          </div>

          {/* System Status Pill */}
          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60">
              <span className="status-beacon"></span>
              <span className="text-slate-300 font-medium">Engine Active</span>
              <span className="text-slate-600">|</span>
              <span className="text-emerald-400 font-mono">Flask 3.1 & ML</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-800/60 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn whitespace-nowrap ${isActive ? 'active' : ''}`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
