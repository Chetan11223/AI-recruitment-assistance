import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Sparkles, User, Bot, ChevronDown, ChevronRight, 
  ExternalLink, ShieldCheck, HelpCircle, Layers 
} from 'lucide-react';
import { queryAgent } from '../api/client';

export default function RecruiterChat({ selectedJobId, candidates, jobs }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I am your AI Recruitment Reasoning Assistant. I navigate candidate resumes via structure-aware PageIndex trees rather than flat vector embeddings, providing grounded, explainable answers with direct resume citations.\n\nHow can I assist you with screening or candidate comparison today?",
      traversal_steps: [],
      cited_evidence: [],
      suggested_followups: [
        "Who has the most experience with Kafka and distributed systems?",
        "Compare Alex Rivera and Elena Rostova",
        "Rank all candidates against the active JD"
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [openSteps, setOpenSteps] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryAgent({
        query: text,
        job_id: selectedJobId || undefined,
        conversation_history: messages.map(m => ({ role: m.role, content: m.content }))
      });

      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        traversal_steps: response.traversal_steps || [],
        cited_evidence: response.cited_evidence || [],
        suggested_followups: response.suggested_followups || []
      };

      setMessages((prev) => [...prev, assistantMsg]);
      // Auto open reasoning steps for new message
      setOpenSteps((prev) => ({ ...prev, [messages.length + 1]: true }));
    } catch (err) {
      console.error('Chat error', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your query. Please check your backend connection.',
          traversal_steps: [],
          cited_evidence: [],
          suggested_followups: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSteps = (idx) => {
    setOpenSteps((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl flex flex-col h-[750px] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800 bg-slate-800/40 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Recruiter AI Reasoning Agent</h3>
            <p className="text-[11px] text-slate-400">PageIndex Multi-Tree Traversal & Cross-Document Synthesis</p>
          </div>
        </div>

        <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Agentic RAG Active
        </span>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          return (
            <div key={idx} className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                isUser ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-indigo-400 border border-slate-700'
              }`}>
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className={`max-w-2xl space-y-3 ${isUser ? 'items-end' : ''}`}>
                {/* Message Bubble */}
                <div className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/60 shadow-md'
                }`}>
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>

                {/* Traversal Steps (Collapsible) */}
                {!isUser && msg.traversal_steps && msg.traversal_steps.length > 0 && (
                  <div className="bg-slate-950/60 border border-slate-800 rounded-xl overflow-hidden">
                    <button
                      onClick={() => toggleSteps(idx)}
                      className="w-full px-3 py-2 text-left flex items-center justify-between text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
                    >
                      <div className="flex items-center space-x-2">
                        <Layers className="w-3.5 h-3.5 text-indigo-400" />
                        <span>Agent Traversal & Reasoning Trace ({msg.traversal_steps.length} steps)</span>
                      </div>
                      {openSteps[idx] ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>

                    {openSteps[idx] && (
                      <div className="p-3 border-t border-slate-800/80 space-y-2 bg-slate-900/40">
                        {msg.traversal_steps.map((step, sIdx) => (
                          <div key={sIdx} className="text-[11px] bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                            <div className="flex items-center space-x-2 font-mono text-indigo-300">
                              <span>Step #{step.step_num}:</span>
                              <span className="font-bold text-slate-200">{step.action}</span>
                            </div>
                            <p className="text-slate-400 mt-1">{step.reasoning}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Grounded Citations */}
                {!isUser && msg.cited_evidence && msg.cited_evidence.length > 0 && (
                  <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-3 space-y-1.5">
                    <div className="flex items-center space-x-1.5 text-[10px] font-bold text-indigo-400 uppercase tracking-wider">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Grounded Citations ({msg.cited_evidence.length})</span>
                    </div>
                    <div className="space-y-1">
                      {msg.cited_evidence.slice(0, 3).map((cit, cIdx) => (
                        <div key={cIdx} className="text-[11px] bg-slate-900/80 p-2 rounded border border-slate-800 text-slate-300 font-mono">
                          <span className="text-indigo-400 font-semibold">[Pg {cit.page_number}]</span> "{cit.raw_text}"
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggested Followups */}
                {!isUser && msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div className="flex items-center flex-wrap gap-1.5 pt-1">
                    {msg.suggested_followups.map((sug, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => handleSend(sug)}
                        className="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 px-2.5 py-1 rounded-full transition text-left"
                      >
                        ⚡ {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-slate-800 text-indigo-400 border border-slate-700 flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-800/90 border border-slate-700/60 p-4 rounded-2xl max-w-md">
              <div className="flex items-center space-x-2 text-xs text-indigo-300 animate-pulse">
                <Sparkles className="w-4 h-4" />
                <span>Traversing PageIndex tree nodes & aggregating evidence...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-slate-800 bg-slate-800/30">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Ask anything about candidates, compare profiles, or request ranking..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-500/25 transition shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
