import React, { useState, useEffect } from 'react';
import { 
  History, Search, Filter, ShieldAlert, ShieldCheck, 
  ExternalLink, Trash2, Eye, X, RefreshCw 
} from 'lucide-react';
import { getHistory, clearAuditHistory } from '../utils/api';

export default function RecentScansTable({ onScanCompleted }) {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [riskFilter, setRiskFilter] = useState('');
  const [search, setSearch] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const params = {};
      if (riskFilter) params.risk_level = riskFilter;
      if (search) params.search = search;
      const data = await getHistory(params);
      setRecords(data.records || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error('Failed to load history:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [riskFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRecords();
  };

  const handleClear = async () => {
    if (!window.confirm('Reset audit log database? (This will clear all past scans)')) return;
    try {
      await clearAuditHistory();
      fetchRecords();
      if (onScanCompleted) onScanCompleted();
    } catch (e) {
      alert('Error clearing logs');
    }
  };

  const getRiskBadge = (level, score) => {
    switch (level) {
      case 'HIGH':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold badge-high">{score} / High</span>;
      case 'SUSPICIOUS':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold badge-suspicious">{score} / Suspicious</span>;
      case 'CAUTION':
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold badge-caution">{score} / Caution</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-xs font-bold badge-safe">{score} / Safe</span>;
    }
  };

  return (
    <div className="space-y-4">
      {/* Search & Filter Toolbar */}
      <div className="cyber-card p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 w-full md:w-auto flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search sanitized message snippets..."
              className="w-full pl-9 pr-3 py-1.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-all"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-2 w-full md:w-auto justify-between md:justify-end">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none"
            >
              <option value="">All Risk Levels</option>
              <option value="HIGH">High Risk</option>
              <option value="SUSPICIOUS">Suspicious</option>
              <option value="CAUTION">Caution</option>
              <option value="LOW">Likely Safe</option>
            </select>
          </div>

          <button
            onClick={fetchRecords}
            title="Refresh"
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={handleClear}
            title="Reset Audit History"
            className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-xs flex items-center gap-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="cyber-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Anonymized Hash</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Masked Content</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading && records.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-8 text-center text-slate-500">
                    Loading audit trail...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-8 text-center text-slate-500">
                    No scans match the current filter criteria.
                  </td>
                </tr>
              ) : (
                records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono text-[11px]">
                      {r.created_at ? new Date(r.created_at).toLocaleTimeString() : '--'}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                        {r.source}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-400 text-[11px]">
                      {r.user_identifier_hash}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-200">{r.classification}</div>
                      <div className="text-[10px] text-slate-400 truncate max-w-xs">{r.category}</div>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getRiskBadge(r.risk_level, r.risk_score)}
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono text-[11px] max-w-xs truncate">
                      {r.masked_content_snippet || '--'}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={() => setSelectedRecord(r)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-1 cursor-pointer"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="py-2.5 px-4 bg-slate-950/60 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Showing {records.length} of {total} audit records</span>
          <span>Zero plaintext phone numbers stored (Privacy by Design)</span>
        </div>
      </div>

      {/* Forensic Inspection Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="cyber-card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto space-y-4 border-slate-700">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">Forensic Audit Inspection</span>
                <span className="text-xs font-mono text-slate-400">ID #{selectedRecord.id}</span>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Risk Score</span>
                <span className="text-xl font-bold font-mono text-emerald-400">{selectedRecord.risk_score} / 100</span>
                <span className="text-[11px] text-slate-400 block mt-1">{selectedRecord.risk_level} Band</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-400 block mb-1">Classification</span>
                <span className="text-sm font-bold text-white">{selectedRecord.classification}</span>
                <span className="text-[11px] text-slate-400 block mt-1">{selectedRecord.category}</span>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Sanitized Content Snippet</span>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200">
                {selectedRecord.masked_content_snippet}
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Detected Indicators</span>
              <ul className="space-y-1 text-xs text-slate-300">
                {(selectedRecord.detected_indicators || []).map((ind, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="text-rose-400 font-bold">•</span>
                    <span>{ind}</span>
                  </li>
                ))}
              </ul>
            </div>

            {selectedRecord.urls_detected?.length > 0 && (
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Extracted URLs</span>
                <div className="space-y-1">
                  {selectedRecord.urls_detected.map((u, i) => (
                    <div key={i} className="p-2 rounded bg-slate-950 text-xs font-mono text-cyan-300 truncate">
                      {u}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Automated Explanation</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                {selectedRecord.explanation_summary}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedRecord(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-medium cursor-pointer"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
