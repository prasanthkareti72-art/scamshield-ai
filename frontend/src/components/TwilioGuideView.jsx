import React, { useState } from 'react';
import { BookOpen, Copy, Check, ExternalLink, Terminal, Shield, ArrowRight } from 'lucide-react';

export default function TwilioGuideView() {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyCode = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const steps = [
    {
      title: '1. Join the Twilio WhatsApp Sandbox',
      desc: 'Twilio provides a free sandbox for testing WhatsApp bots without needing full Meta Business approval.',
      code: 'Send WhatsApp message:\njoin <your-sandbox-word>\nTo: +1 415 523 8886',
      notes: 'Find your specific sandbox join keyword inside your Twilio Console (Messaging > WhatsApp Sandbox).'
    },
    {
      title: '2. Expose Local Flask Backend via Tunnel (ngrok or Cloudflare)',
      desc: 'Twilio webhooks need a public HTTPS URL to reach your local Flask server.',
      code: 'ngrok http 5000',
      notes: 'Copy the resulting forwarding URL (e.g. https://a1b2-c3d4.ngrok-free.app).'
    },
    {
      title: '3. Set the Inbound Webhook URL in Twilio',
      desc: 'In Twilio Console -> WhatsApp Sandbox Settings -> "When a message comes in":',
      code: 'https://<your-ngrok-url>/api/webhook/whatsapp\nMethod: HTTP POST',
      notes: 'Twilio will now send all incoming user WhatsApp messages directly to ScamShield AI.'
    },
    {
      title: '4. Environment Configuration (.env)',
      desc: 'Ensure your backend .env includes credentials if signature validation or outbound messaging is used:',
      code: `TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=+14155238886
VERIFY_TWILIO_SIGNATURE=False`,
      notes: 'Keep VERIFY_TWILIO_SIGNATURE=False while testing locally with ngrok, set to True in production.'
    }
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="cyber-card p-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-emerald-400" />
          Twilio WhatsApp Sandbox Setup Guide
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Follow these quick steps to connect your real phone via WhatsApp to the ScamShield AI backend.
        </p>
      </div>

      {/* Step by step cards */}
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <div key={idx} className="cyber-card p-5 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-xs font-mono font-bold">
                    {idx + 1}
                  </span>
                  {step.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1 pl-8">
                  {step.desc}
                </p>
              </div>
            </div>

            <div className="pl-8 space-y-2">
              <div className="relative group">
                <pre className="p-3 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-emerald-300 overflow-x-auto">
                  {step.code}
                </pre>
                <button
                  onClick={() => copyCode(step.code, idx)}
                  className="absolute right-2 top-2 p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1 cursor-pointer transition-all"
                >
                  {copiedIndex === idx ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-[10px]">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span className="text-[10px]">Copy</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-[11px] text-slate-500 italic">
                💡 {step.notes}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Zero Twilio Setup Fallback */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 space-y-2">
        <h4 className="font-semibold text-white flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          No Twilio account? No problem!
        </h4>
        <p className="text-slate-400 leading-relaxed">
          You don't need active Twilio credentials to test the full end-to-end chatbot. The 
          <strong> WhatsApp Simulator</strong> tab runs the identical production NLP analysis, risk scoring, and response formatting pipeline in your browser!
        </p>
      </div>
    </div>
  );
}
