import React, { useState, useEffect } from 'react';
import { X, Award, Check, AlertTriangle, ExternalLink, ShieldCheck, FileText, ChevronRight } from 'lucide-react';
import { getScorecard } from '../api/client';

export default function ScorecardModal({ isOpen, onClose, candidate, job }) {
  const [scorecard, setScorecard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState(null);

  useEffect(() => {
    if (isOpen && candidate && job) {
      loadScorecard();
    }
  }, [isOpen, candidate, job]);

  const loadScorecard = async () => {
    setLoading(true);
    try {
      const data = await getScorecard(candidate.candidate_id, job.job_id);
      setScorecard(data);
    } catch (err) {
      console.error('Failed to load scorecard', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !candidate || !job) return null;

  const getFitBadge = (fitLevel) => {
    if (fitLevel === 'Strong Match') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    if (fitLevel === 'Good Match') return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    if (fitLevel === 'Moderate Match') return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-800/40">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold">
              {candidate.candidate_name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white">{candidate.candidate_name}</h3>
                {scorecard && (
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getFitBadge(scorecard.fit_level)}`}>
                    {scorecard.fit_level}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400">Target Role: <span className="text-slate-200">{job.title}</span></p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {scorecard && (
              <div className="text-right">
                <div className="text-2xl font-black text-white">{scorecard.overall_score}<span className="text-xs font-normal text-slate-400">/100</span></div>
                <div className="text-[10px] text-indigo-400 uppercase font-semibold">Overall Fit Score</div>
              </div>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-sm">Calculating grounded scorecard from PageIndex tree...</p>
            </div>
          ) : scorecard ? (
            <>
              {/* Executive Summary */}
              <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                <span className="text-xs font-bold uppercase text-indigo-400 tracking-wider">Executive Synthesis</span>
                <p className="text-sm text-slate-200 mt-1 leading-relaxed">{scorecard.executive_summary}</p>
              </div>

              {/* 4 Dimensions Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(scorecard.dimension_scores).map(([key, dim]) => (
                  <div key={key} className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-4 flex flex-col justify-between space-y-3">
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                          {dim.dimension_name}
                        </span>
                        <div className="text-right">
                          <span className="text-sm font-bold text-white">{dim.raw_score}%</span>
                          <span className="text-[10px] text-slate-400 ml-1">({(dim.weight * 100).toFixed(0)}% weight)</span>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full h-1.5 bg-slate-700 rounded-full mt-2 overflow-hidden">
                        <div 
                          className="h-full bg-indigo-500 rounded-full transition-all duration-500" 
                          style={{ width: `${dim.raw_score}%` }} 
                        />
                      </div>

                      <p className="text-xs text-slate-300 mt-2.5 leading-relaxed">{dim.rationale}</p>
                    </div>

                    {/* Matched & Missing Chips */}
                    <div className="space-y-1.5 pt-2 border-t border-slate-700/50">
                      {dim.matched_items && dim.matched_items.length > 0 && (
                        <div className="flex items-start space-x-1.5 flex-wrap gap-y-1">
                          <Check className="w-3 h-3 text-emerald-400 mt-0.5 shrink-0" />
                          <div className="flex flex-wrap gap-1">
                            {dim.matched_items.map((item, idx) => (
                              <span key={idx} className="text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                                {item}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {dim.missing_items && dim.missing_items.length > 0 && (
                        <div className="flex items-start space-x-1.5 flex-wrap gap-y-1">
                          <AlertTriangle className="w-3 h-3 text-amber-400 mt-0.5 shrink-0" />
                          <div className="flex flex-wrap gap-1">
                            {dim.missing_items.map((item, idx) => (
                              <span key={idx} className="text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20 px-1.5 py-0.5 rounded">
                                Missing: {item}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Cited Evidence Buttons */}
                    {dim.cited_spans && dim.cited_spans.length > 0 && (
                      <div className="pt-2">
                        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Grounded Citations:</span>
                        <div className="flex flex-wrap gap-1.5">
                          {dim.cited_spans.map((cit, idx) => (
                            <button
                              key={idx}
                              onClick={() => setSelectedCitation(cit)}
                              className="text-[10px] flex items-center space-x-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded transition"
                            >
                              <ExternalLink className="w-2.5 h-2.5" />
                              <span>Pg {cit.page_number} Citation</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Citation Viewer Modal Drawer */}
              {selectedCitation && (
                <div className="p-4 bg-slate-950 border border-indigo-500/40 rounded-xl space-y-2 animate-in fade-in">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400 flex items-center space-x-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>Verified Resume Source Quote (Page {selectedCitation.page_number})</span>
                    </span>
                    <button onClick={() => setSelectedCitation(null)} className="text-slate-400 hover:text-white text-xs">
                      Close
                    </button>
                  </div>
                  <p className="text-xs font-mono text-slate-300 bg-slate-900/80 p-3 rounded-lg border border-slate-800 whitespace-pre-wrap">
                    "{selectedCitation.raw_text}"
                  </p>
                </div>
              )}
            </>
          ) : (
            <p className="text-center text-sm text-slate-400">Failed to load scorecard.</p>
          )}
        </div>
      </div>
    </div>
  );
}
