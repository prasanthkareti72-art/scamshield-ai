import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, AlertTriangle, Database, Shield, Layers, BookCheck } from 'lucide-react';
import { getRulesAndMetrics } from '../utils/api';

export default function ModelMetricsView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRulesAndMetrics()
      .then(setData)
      .catch((e) => console.error('Failed to load model metrics:', e))
      .finally(() => setLoading(false));
  }, []);

  const models = data?.model_metrics?.models || {};
  const fakeNewsModel = models.fake_news;
  const scamModel = models.scam_phishing;
  const categories = data?.rules_engine?.categories || {};

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="cyber-card p-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-emerald-400" />
          AI / NLP Models & Detection Rule Architecture
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Complete algorithmic transparency: Evaluated using scikit-learn stratified train/test validation, TF-IDF feature extraction, and explainable multi-signal fusion.
        </p>
      </div>

      {/* ML Evaluation Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fake News Model Card */}
        <div className="cyber-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                NLP Text Classifier
              </span>
              <h3 className="text-sm font-bold text-white mt-1">
                Fake News & Misinformation Classifier
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-400">TF-IDF + Logistic Regression</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {fakeNewsModel ? `${(fakeNewsModel.accuracy * 100).toFixed(1)}%` : '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">F1 Score</span>
              <span className="text-xl font-bold font-mono text-cyan-400">
                {fakeNewsModel?.f1_score ?? '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Precision</span>
              <span className="text-xl font-bold font-mono text-purple-400">
                {fakeNewsModel?.precision ?? '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Recall</span>
              <span className="text-xl font-bold font-mono text-amber-400">
                {fakeNewsModel?.recall ?? '--'}
              </span>
            </div>
          </div>

          {fakeNewsModel?.confusion_matrix && (
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                Confusion Matrix (Test Evaluation)
              </span>
              <div className="grid grid-cols-2 gap-2 text-center font-mono">
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">True Negative (Genuine)</span>
                  <span className="text-sm font-bold text-slate-200">{fakeNewsModel.confusion_matrix.tn}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">False Positive</span>
                  <span className="text-sm font-bold text-rose-400">{fakeNewsModel.confusion_matrix.fp}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">False Negative</span>
                  <span className="text-sm font-bold text-rose-400">{fakeNewsModel.confusion_matrix.fn}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">True Positive (Hoax)</span>
                  <span className="text-sm font-bold text-emerald-400">{fakeNewsModel.confusion_matrix.tp}</span>
                </div>
              </div>
            </div>
          )}

          <div className="text-[11px] text-slate-400 space-y-1">
            <p>• Features: Unigrams & Bigrams with sublinear term frequency scaling</p>
            <p>• Cross-Reference: Fact-checking registry match automatically overrides ML prediction</p>
          </div>
        </div>

        {/* Scam & Phishing Model Card */}
        <div className="cyber-card p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-cyan-400 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                Fraud & Phishing Model
              </span>
              <h3 className="text-sm font-bold text-white mt-1">
                Scam & Phishing Message Classifier
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-400">TF-IDF + Logistic Regression</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {scamModel ? `${(scamModel.accuracy * 100).toFixed(1)}%` : '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">F1 Score</span>
              <span className="text-xl font-bold font-mono text-cyan-400">
                {scamModel?.f1_score ?? '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Precision</span>
              <span className="text-xl font-bold font-mono text-purple-400">
                {scamModel?.precision ?? '--'}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Recall</span>
              <span className="text-xl font-bold font-mono text-amber-400">
                {scamModel?.recall ?? '--'}
              </span>
            </div>
          </div>

          {scamModel?.confusion_matrix && (
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                Confusion Matrix (Test Evaluation)
              </span>
              <div className="grid grid-cols-2 gap-2 text-center font-mono">
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">True Negative (Safe)</span>
                  <span className="text-sm font-bold text-slate-200">{scamModel.confusion_matrix.tn}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">False Positive</span>
                  <span className="text-sm font-bold text-rose-400">{scamModel.confusion_matrix.fp}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">False Negative</span>
                  <span className="text-sm font-bold text-rose-400">{scamModel.confusion_matrix.fn}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">True Positive (Scam)</span>
                  <span className="text-sm font-bold text-emerald-400">{scamModel.confusion_matrix.tp}</span>
                </div>
              </div>
            </div>
          )}

          <div className="text-[11px] text-slate-400 space-y-1">
            <p>• Features: Financial urgency tokens, payment gateway cues, OTP extraction</p>
            <p>• Hybrid Fusion: Multi-signal weighted formula combines ML with regex heuristics</p>
          </div>
        </div>
      </div>

      {/* Rule Categories Table */}
      <div className="cyber-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            Configured Scam Pattern Heuristics & Severity Weights
          </h3>
          <span className="text-xs font-mono text-slate-400">{Object.keys(categories).length} Categories</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {Object.entries(categories).map(([key, cat]) => (
            <div key={key} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{cat.name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  cat.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' :
                  cat.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-300' :
                  'bg-amber-500/20 text-amber-300'
                }`}>
                  {cat.severity} (Base {cat.base_risk})
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                {cat.description}
              </p>
              <div className="pt-2 border-t border-slate-800/60 flex flex-wrap gap-1">
                {(cat.keywords || []).slice(0, 4).map((kw, idx) => (
                  <span key={idx} className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-slate-400 border border-slate-800">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fact-Checking Accredited Sources */}
      <div className="cyber-card p-6 space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <BookCheck className="w-4 h-4 text-purple-400" />
          Integrated Fact-Checking Repositories & Protocols
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          ScamShield AI adheres strictly to the rule of <strong>never fabricating fact-checking results</strong>.
          Claims are verified against:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <strong className="text-white block">PIB Fact Check</strong>
            <span className="text-[11px] text-slate-400">Government of India official debunks</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <strong className="text-white block">BoomLive & AltNews</strong>
            <span className="text-[11px] text-slate-400">IFCN certified independent verification</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <strong className="text-white block">Snopes & Reuters</strong>
            <span className="text-[11px] text-slate-400">International debunk archive</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <strong className="text-white block">Google ClaimReview API</strong>
            <span className="text-[11px] text-slate-400">Live search against global fact-checks</span>
          </div>
        </div>
      </div>
    </div>
  );
}
