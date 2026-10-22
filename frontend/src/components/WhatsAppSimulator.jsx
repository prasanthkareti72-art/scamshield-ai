import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Shield, CheckCheck, RefreshCw, MessageSquare, AlertTriangle, 
  Smartphone, Sparkles, User, CornerDownLeft
} from 'lucide-react';
import { simulateWhatsApp } from '../utils/api';

const QUICK_CHATS = [
  {
    title: '🏦 SBI KYC Freeze',
    msg: 'Dear customer, your SBI account KYC has expired. Your netbanking access will be blocked tonight at 9:30 PM. Update your PAN card now: http://sbi-kyc-verify-portal.top'
  },
  {
    title: '🎁 ₹50,000 Prize',
    msg: 'Congratulations! You won ₹50,000 in Kaun Banega Crorepati WhatsApp Lucky Draw! Click http://kbc-lucky-winner.xyz/claim immediately and forward this message to 10 people to claim your prize.'
  },
  {
    title: '💼 Work-From-Home Task',
    msg: 'Earn ₹3,500 to ₹7,000 daily from home! Like YouTube videos and review hotels on Google Maps. No experience needed. Daily payouts via UPI. Message Telegram: t.me/fast_earning_vip'
  },
  {
    title: '📰 NASA Darkness Fake News',
    msg: 'ALERT: NASA confirms Earth will be in 6 full days of total darkness starting next Monday due to solar storm! Prepare candles now! Forward to save a life!'
  },
  {
    title: '🟢 Normal Dinner Meeting',
    msg: 'Hey Rohan, we have booked the table for dinner tonight at 8:00 PM. See you and family there!'
  }
];

export default function WhatsAppSimulator({ onScanCompleted }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'user',
      text: 'Congratulations! You won ₹50,000. Click http://kbc-winner.xyz immediately and forward this message to 10 people to claim your prize.',
      time: '11:42 AM'
    },
    {
      id: 2,
      sender: 'bot',
      text: `🛡️ *ScamShield AI Analysis*

⚠️ Risk Level: HIGH

📊 *Estimated Risk Score:* 92/100

🔎 *Category:* Possible Prize Scam

🔗 Link Security: High-Risk Phishing Link Detected (Risk: 85/100)

🚩 *Warning Signs:*
• Unexpected cash prize
• Urgent call to action
• Requests forwarding to multiple contacts
• Deceptive domain impersonating brand without official ownership

✅ *Safety Advice:*
• Do not click the link.
• Do not share OTPs, passwords, or banking information.
• Verify the offer through the company's official website.

ℹ️ *Confidence:* High
_Note: This is an automated risk assessment, not a definitive finding. Always exercise personal vigilance._`,
      time: '11:42 AM'
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputMessage;
    if (!text.trim() || loading) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append user message
    const userMsgObj = {
      id: Date.now(),
      sender: 'user',
      text: text.trim(),
      time: currentTime
    };

    setMessages((prev) => [...prev, userMsgObj]);
    setInputMessage('');
    setLoading(true);

    try {
      const data = await simulateWhatsApp(text.trim(), '+919876543210');
      const botMsgObj = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.bot_reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        analysis: data.analysis
      };
      setMessages((prev) => [...prev, botMsgObj]);
      if (onScanCompleted) {
        onScanCompleted();
      }
    } catch (err) {
      const errorMsgObj = {
        id: Date.now() + 1,
        sender: 'bot',
        text: '🛡️ *ScamShield AI*: Service temporarily unavailable. Please verify backend connection.',
        time: currentTime
      };
      setMessages((prev) => [...prev, errorMsgObj]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      {/* Simulation Info Banner */}
      <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>
            <strong>Interactive WhatsApp Sandbox:</strong> Test the exact Twilio chatbot webhook pipeline without needing external credentials!
          </span>
        </div>
        <button
          onClick={() => setMessages([])}
          className="text-xs text-emerald-400 hover:text-emerald-200 underline whitespace-nowrap cursor-pointer"
        >
          Reset Chat
        </button>
      </div>

      {/* Quick Test Forward Chips */}
      <div>
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
          Quick-Forward Suspicious Messages:
        </span>
        <div className="flex flex-wrap gap-2">
          {QUICK_CHATS.map((qc, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading}
              onClick={() => handleSendMessage(qc.msg)}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/70 text-slate-300 hover:text-white transition-all disabled:opacity-50 cursor-pointer"
            >
              {qc.title}
            </button>
          ))}
        </div>
      </div>

      {/* WhatsApp Web Container */}
      <div className="wa-container flex flex-col h-[600px]">
        {/* WhatsApp Chat Header */}
        <div className="bg-[#202c33] px-4 py-3 flex items-center justify-between border-b border-[#2a3942] z-10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-emerald-700/80 flex items-center justify-center text-white font-bold border border-emerald-500/40 relative">
              <Shield className="w-5 h-5 text-emerald-300" />
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#202c33]" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-sm font-semibold text-white">ScamShield AI</span>
                <span className="w-3.5 h-3.5 bg-emerald-500 rounded-full flex items-center justify-center text-[9px] text-slate-950 font-bold" title="Verified Security Bot">
                  ✓
                </span>
              </div>
              <p className="text-[11px] text-emerald-400">
                {loading ? 'Analyzing security signals...' : 'Online • Automated Risk Analyzer'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[11px] font-mono text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-full border border-slate-700/60">
              Twilio Webhook Live
            </span>
          </div>
        </div>

        {/* Chat History Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {/* E2E Encryption Banner */}
          <div className="text-center">
            <span className="inline-block text-[11px] text-amber-200/80 bg-[#182229] px-3 py-1.5 rounded-lg border border-amber-500/20 shadow-sm max-w-md">
              🔒 Messages forwarded to ScamShield AI are scanned via privacy-preserving NLP. No personal identity is stored.
            </span>
          </div>

          {messages.map((m) => {
            const isUser = m.sender === 'user';
            return (
              <div
                key={m.id}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[75%] p-3.5 shadow-md ${
                    isUser ? 'wa-bubble-out' : 'wa-bubble-in'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed font-sans select-text">
                    {m.text}
                  </div>
                  <div className="flex items-center justify-end space-x-1 mt-1 text-[10px] text-slate-400 select-none">
                    <span>{m.time}</span>
                    {isUser && <CheckCheck className="w-3.5 h-3.5 text-cyan-400" />}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="wa-bubble-in px-4 py-2.5 rounded-xl flex items-center space-x-2 text-xs text-slate-300">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                <span>ScamShield AI is analyzing the submitted content...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input Bar */}
        <div className="bg-[#202c33] p-3 border-t border-[#2a3942] flex items-center gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSendMessage();
            }}
            placeholder="Type or paste suspicious WhatsApp message..."
            disabled={loading}
            className="flex-1 bg-[#2a3942] text-white placeholder-slate-400 text-sm px-4 py-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
          />
          <button
            type="button"
            onClick={() => handleSendMessage()}
            disabled={loading || !inputMessage.trim()}
            className="w-10 h-10 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 flex items-center justify-center text-white transition-all cursor-pointer flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
