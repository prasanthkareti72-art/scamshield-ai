import React, { useState } from 'react';
import { 
  ShieldAlert, ShieldCheck, AlertTriangle, AlertCircle, 
  ExternalLink, CheckCircle2, Copy, Check, Sparkles, RefreshCw, Eye
} from 'lucide-react';
import { analyzeContent } from '../utils/api';

const SAMPLE_PRESETS = [
  {
    label: '🏦 SBI KYC Scam',
    type: 'scam',
    text: 'Dear customer, your SBI account KYC has expired. Your netbanking access will be blocked tonight at 9:30 PM. Update your PAN card now to avoid deactivation: http://sbi-kyc-verify-portal.top'
  },
  {
    label: '🎁 ₹50,000 KBC Prize',
    type: 'scam',
    text: 'Congratulations! You won ₹50,000 cash prize in Kaun Banega Crorepati WhatsApp Lucky Draw! Click http://kbc-lucky-winner.xyz/claim immediately and forward to 10 contacts to claim.'
  },
  {
    label: '💼 Part-Time Task Scam',
    type: 'scam',
    text: 'Work from home: Earn ₹4,000 to ₹8,000 daily just by liking YouTube videos and rating hotels on Google Maps. No experience needed. Instant daily payouts via UPI. Contact on Telegram: t.me/fast_earning_vip'
  },
  {
    label: '📰 NASA Darkness Hoax',
    type: 'fake_news',
    text: 'BREAKING: NASA confirmed Earth will plunge into 6 full days of total darkness starting next Monday due to an unprecedented solar storm! Prepare candles now! Forward to save a life!'
  },
  {
    label: '⚡ Electricity Cut Scam',
    type: 'scam',
    text: 'Urgent notice: Your electricity power will be disconnected at 9:30 PM tonight from electricity head office because your previous month bill was not updated. Please contact electricity officer immediately at 9811223344'
  },
  {
    label: '🏥 Boiled Garlic Hoax',
    type: 'fake_news',
    text: 'BREAKING: Government has ordered all citizens to immediately drink boiled garlic and lemon water every morning to become 100% immune to all respiratory viruses! Forward to everyone!'
  },
  {
    label: '🟢 Benign Meeting Note',
    type: 'safe',
    text: 'Hey Priya, the monthly project review meeting is rescheduled to Thursday 3:00 PM in Conference Room B. Please review the updated agenda on the shared drive.'
  }
];

export default function LiveScanner({ onScanCompleted }) {
  const [inputText, setInputText] = useState(SAMPLE_PRESETS[0].text);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [showWhatsAppView, setShowWhatsAppView] = useState(false);

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await analyzeContent(inputText.trim(), 'web_dashboard');
      setResult(data);
      if (onScanCompleted) {
        onScanCompleted();
      }
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check backend connectivity.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyWhatsApp = () => {
    if (!result?.whatsapp_preview) return;
    navigator.clipboard.writeText(result.whatsapp_preview);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper for risk color
  const getRiskColor = (score) => {
    if (score >= 75) return { text: 'text-rose-400', bg: 'bg-rose-500', border: 'border-rose-500/40', badge: 'badge-high' };
    if (score >= 50) return { text: 'text-orange-400', bg: 'bg-orange-500', border: 'border-orange-500/40', badge: 'badge-suspicious' };
    if (score >= 25) return { text: 'text-amber-400', bg: 'bg-amber-500', border: 'border-amber-500/40', badge: 'badge-caution' };
    return { text: 'text-emerald-400', bg: 'bg-emerald-500', border: 'border-emerald-500/40', badge: 'badge-safe' };
  };

  const analysis = result?.analysis;
  const riskColor = analysis ? getRiskColor(analysis.estimated_risk_score) : null;

  return (
    <div className="space-y-6">
      {/* Input Console */}
      <div className="cyber-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-400" />
              Live Security Threat Analyzer
            </h2>
            <p className="text-xs text-slate-400">
              Submit suspicious text messages, WhatsApp forwards, viral news claims, or URLs for instant NLP risk scoring.
            </p>
          </div>
          <button
            onClick={() => setInputText('')}
            className="text-xs text-slate-400 hover:text-slate-200 self-start md:self-center"
          >
            Clear Input
          </button>
        </div>

        {/* Preset Chips */}
        <div className="mt-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            One-Click Sample Presets:
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setInputText(preset.text);
                  setResult(null);
                }}
                className={`text-xs px-2.5 py-1.5 rounded-lg border transition-all ${
                  inputText === preset.text
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-medium'
                    : 'bg-slate-800/60 border-slate-700/60 text-slate-300 hover:bg-slate-800 hover:border-slate-600'
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        {/* Text Form */}
        <form onSubmit={handleAnalyze} className="mt-4 space-y-4">
          <div>
            <textarea
              rows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste suspicious text message, WhatsApp forward, news claim, or link here..."
              className="w-full px-4 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500/70 focus:ring-1 focus:ring-emerald-500/50 font-mono text-sm leading-relaxed"
            />
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <span className="text-xs text-slate-400">
              Chars: <span className="font-mono text-slate-200">{inputText.length}</span> | Zero PII persisted to disk
            </span>
            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold rounded-xl shadow-lg shadow-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm transition-all cursor-pointer"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                  <span>Evaluating Risk Signals...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-slate-950" />
                  <span>Run AI Security Scan</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Forensic Report Output */}
      {analysis && (
        <div className="cyber-card p-6 border-slate-700/80 space-y-6">
          {/* Top Risk Header */}
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between pb-6 border-b border-slate-800 gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${riskColor.badge}`}>
                  {analysis.risk_band_label}
                </span>
                <span className="text-xs text-slate-400">
                  Category: <strong className="text-slate-200">{analysis.category}</strong>
                </span>
              </div>
              <h3 className="text-2xl font-bold text-white tracking-tight">
                {analysis.classification}
              </h3>
              <p className="text-xs text-slate-400">
                Confidence: <span className="text-slate-300 font-medium">{analysis.confidence_level}</span>
              </p>
            </div>

            {/* Risk Gauge Metric */}
            <div className="flex items-center gap-4 bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 self-stretch lg:self-auto justify-between lg:justify-start">
              <div>
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Estimated Risk Score
                </span>
                <div className="flex items-baseline gap-1 mt-0.5">
                  <span className={`text-3xl font-extrabold font-mono ${riskColor.text}`}>
                    {analysis.estimated_risk_score}
                  </span>
                  <span className="text-sm font-mono text-slate-500">/100</span>
                </div>
              </div>
              <div className="w-24 h-3 bg-slate-800 rounded-full overflow-hidden p-0.5">
                <div 
                  className={`h-full rounded-full transition-all duration-700 ${riskColor.bg}`}
                  style={{ width: `${analysis.estimated_risk_score}%` }}
                />
              </div>
            </div>
          </div>

          {/* Grid: Warning Signs & Safety Advice */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Warning Signs */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" />
                Detected Threat Indicators ({analysis.warning_signs.length})
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {analysis.warning_signs.map((sign, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-rose-400 font-bold">•</span>
                    <span>{sign}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommended Safety Advice */}
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" />
                Recommended Next Steps
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {analysis.safety_advice.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* URL Security Diagnostics (if links found) */}
          {analysis.url_analysis?.has_urls && (
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <ExternalLink className="w-4 h-4" />
                  URL & Domain Security Diagnostics ({analysis.url_analysis.count} link detected)
                </h4>
                <span className="text-xs font-mono text-slate-400">
                  Highest URL Risk: {analysis.url_analysis.highest_risk_score}/100
                </span>
              </div>
              <div className="space-y-2">
                {analysis.url_analysis.detailed_results.map((urlItem, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-900 border border-slate-800/80 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="space-y-1">
                      <div className="font-mono text-slate-200 truncate max-w-md">
                        {urlItem.url}
                      </div>
                      <div className="flex flex-wrap gap-2 text-[11px] text-slate-400">
                        <span>Host: <strong className="text-slate-300">{urlItem.hostname}</strong></span>
                        <span>SSL: {urlItem.is_https ? '✅ HTTPS' : '⚠️ Insecure HTTP'}</span>
                        {urlItem.is_ip && <span className="text-rose-400 font-bold">⚠️ Raw IP Address</span>}
                        {urlItem.is_shortener && <span className="text-amber-400 font-bold">⚠️ Shortener</span>}
                        {urlItem.spoofed_brand && <span className="text-rose-400 font-bold">⚠️ Brand Spoof: {urlItem.spoofed_brand}</span>}
                      </div>
                    </div>
                    <span className={`px-2.5 py-1 rounded text-[11px] font-bold whitespace-nowrap self-start sm:self-auto ${
                      urlItem.risk_score >= 60 ? 'bg-rose-500/20 text-rose-300' : 'bg-slate-800 text-slate-300'
                    }`}>
                      {urlItem.verdict}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fact-Checking Verification Section (if news claim) */}
          {analysis.fake_news_analysis?.is_news_claim && (
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-2">
                <Eye className="w-4 h-4" />
                Accredited Fact-Checking Registry Cross-Reference
              </h4>
              <div className="text-xs text-slate-300 leading-relaxed">
                {analysis.fake_news_analysis.fact_check_verification.verified_match ? (
                  <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-200 space-y-1">
                    <div className="font-semibold text-rose-300">
                      🚨 Verified Debunk: {analysis.fake_news_analysis.fact_check_verification.verdict}
                    </div>
                    <div>Source: {analysis.fake_news_analysis.fact_check_verification.source}</div>
                    <p className="text-[11px] text-slate-300">{analysis.fake_news_analysis.fact_check_verification.summary}</p>
                  </div>
                ) : (
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 text-[11px]">
                    ℹ️ {analysis.fake_news_analysis.fact_check_verification.summary}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* WhatsApp Preview Toggle */}
          <div className="pt-2 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => setShowWhatsAppView(!showWhatsAppView)}
              className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1.5"
            >
              {showWhatsAppView ? 'Hide WhatsApp Text View' : '👁️ View Raw WhatsApp Chatbot Message Format'}
            </button>
            <button
              type="button"
              onClick={handleCopyWhatsApp}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center gap-1.5 transition-all"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied WhatsApp Message!' : 'Copy WhatsApp Message'}</span>
            </button>
          </div>

          {showWhatsAppView && result?.whatsapp_preview && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-300 whitespace-pre-wrap leading-relaxed">
              {result.whatsapp_preview}
            </div>
          )}

          {/* Legal Disclaimer */}
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60 text-[11px] text-slate-400 leading-normal">
            <strong>Disclaimer:</strong> {analysis.disclaimer}
          </div>
        </div>
      )}
    </div>
  );
}
