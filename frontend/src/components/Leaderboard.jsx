import React, { useState } from 'react';
import { 
  Trophy, Play, CheckCircle2, ChevronRight, BarChart2, 
  Sparkles, AlertCircle, ArrowUpRight, ShieldCheck, UserCheck
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar 
} from 'recharts';

export default function Leaderboard({ 
  jobs, 
  selectedJobId, 
  onSelectJob, 
  candidates, 
  ranking, 
  onRunRanking, 
  rankingInProgress,
  onOpenScorecard 
}) {
  const [viewMode, setViewMode] = useState('cards'); // 'cards' | 'table' | 'charts'
  const activeJob = jobs.find(j => j.job_id === selectedJobId) || jobs[0];

  const getFitBadge = (fitLevel) => {
    if (fitLevel === 'Strong Match') return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    if (fitLevel === 'Good Match') return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    if (fitLevel === 'Moderate Match') return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  };

  const chartData = ranking?.leaderboard?.map(item => ({
    name: item.candidate_name.split(' ')[0],
    overall: item.overall_score,
    skills: item.skills_score,
    experience: item.experience_score,
    projects: item.projects_score,
    education: item.education_score,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Target Job Selector & Ranking Execution Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Active Job Selector */}
          <div className="flex-1 min-w-0">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Target Role / Job Description:</span>
            <div className="flex items-center space-x-3 mt-1.5 flex-wrap gap-y-2">
              <select
                value={activeJob?.job_id || ''}
                onChange={(e) => onSelectJob(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-white text-sm font-semibold rounded-xl px-3.5 py-2 focus:outline-none focus:border-indigo-500 max-w-md"
              >
                {jobs.map((j) => (
                  <option key={j.job_id} value={j.job_id}>
                    {j.title} ({j.company}) — Min {j.min_yoe}y
                  </option>
                ))}
              </select>

              {activeJob && (
                <div className="flex items-center space-x-1.5 flex-wrap gap-1">
                  {activeJob.must_have_skills.slice(0, 4).map((s, idx) => (
                    <span key={idx} className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action Button: Run Agentic Ranking */}
          <button
            onClick={() => onRunRanking(activeJob?.job_id)}
            disabled={rankingInProgress || !activeJob || candidates.length === 0}
            className="flex items-center justify-center space-x-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-medium text-sm px-6 py-2.5 rounded-xl shadow-lg shadow-indigo-500/25 transition disabled:opacity-50 shrink-0"
          >
            {rankingInProgress ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Agentic Reasoning in Progress...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-indigo-200" />
                <span>Rank All Candidates Against JD</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Synthesis & Stats Banner */}
      {ranking && (
        <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between flex-wrap gap-2 mb-2">
            <div className="flex items-center space-x-2">
              <Trophy className="w-5 h-5 text-amber-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Agent Evaluation Synthesis</h3>
            </div>
            <span className="text-xs text-indigo-300">
              Evaluated {ranking.evaluated_candidates_count} candidates
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">{ranking.synthesis_summary}</p>
        </div>
      )}

      {/* View Switcher Controls */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <span>Candidate Leaderboard</span>
          <span className="text-xs font-normal text-slate-400">({ranking?.leaderboard?.length || 0} evaluated)</span>
        </h3>

        <div className="flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/60 text-xs">
          {['cards', 'table', 'charts'].map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-3 py-1 rounded-lg capitalize transition ${
                viewMode === mode
                  ? 'bg-indigo-600 text-white font-medium shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {/* Content Rendering based on ViewMode */}
      {!ranking || ranking.leaderboard.length === 0 ? (
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
          <Trophy className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-slate-300">No Ranking Generated Yet</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            Click "Rank All Candidates Against JD" above to run the PageIndex Agentic RAG evaluation loop.
          </p>
        </div>
      ) : viewMode === 'charts' ? (
        /* Visual Comparative Charts */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Overall Candidate Match Scores
            </h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" domain={[0, 100]} fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} 
                  />
                  <Bar dataKey="overall" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Multi-Dimension Rubric Comparison
            </h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" domain={[0, 100]} fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} 
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar dataKey="skills" fill="#10b981" name="Skills (30%)" />
                  <Bar dataKey="experience" fill="#3b82f6" name="Experience (35%)" />
                  <Bar dataKey="projects" fill="#f59e0b" name="Projects (20%)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : viewMode === 'table' ? (
        /* Leaderboard Table View */
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-800/60 text-slate-400 font-semibold border-b border-slate-700/60">
                <tr>
                  <th className="py-3 px-4">Rank</th>
                  <th className="py-3 px-4">Candidate</th>
                  <th className="py-3 px-4">Fit Level</th>
                  <th className="py-3 px-4">Overall</th>
                  <th className="py-3 px-4">Skills (30%)</th>
                  <th className="py-3 px-4">Exp (35%)</th>
                  <th className="py-3 px-4">Projects (20%)</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {ranking.leaderboard.map((item) => (
                  <tr key={item.candidate_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4 font-bold text-white">
                      {item.rank === 1 ? '🥇 #1' : item.rank === 2 ? '🥈 #2' : item.rank === 3 ? '🥉 #3' : `#${item.rank}`}
                    </td>
                    <td className="py-3 px-4 font-semibold text-white">{item.candidate_name}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full font-medium ${getFitBadge(item.fit_level)}`}>
                        {item.fit_level}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-bold text-indigo-400">{item.overall_score}%</td>
                    <td className="py-3 px-4">{item.skills_score}%</td>
                    <td className="py-3 px-4">{item.experience_score}%</td>
                    <td className="py-3 px-4">{item.projects_score}%</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onOpenScorecard(item, activeJob)}
                        className="text-xs text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20 hover:bg-indigo-500/20 transition"
                      >
                        Scorecard
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Leaderboard Cards View */
        <div className="space-y-4">
          {ranking.leaderboard.map((item) => (
            <div
              key={item.candidate_id}
              className="bg-slate-900/80 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 shadow-xl transition-all"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                {/* Rank & Candidate Info */}
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center font-black text-lg ${
                    item.rank === 1
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-lg shadow-amber-500/10'
                      : item.rank === 2
                      ? 'bg-slate-300/20 text-slate-200 border border-slate-400/40'
                      : item.rank === 3
                      ? 'bg-amber-700/20 text-amber-400 border border-amber-700/40'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}>
                    #{item.rank}
                  </div>

                  <div>
                    <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                      <h4 className="text-base font-bold text-white">{item.candidate_name}</h4>
                      <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${getFitBadge(item.fit_level)}`}>
                        {item.fit_level}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{item.comparative_notes}</p>
                  </div>
                </div>

                {/* Score & View Button */}
                <div className="flex items-center space-x-4 self-end md:self-center">
                  <div className="text-right">
                    <div className="text-2xl font-black text-white">{item.overall_score}%</div>
                    <div className="text-[10px] text-slate-400 uppercase font-semibold">Match Score</div>
                  </div>
                  <button
                    onClick={() => onOpenScorecard(item, activeJob)}
                    className="flex items-center space-x-1 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl shadow-lg shadow-indigo-500/20 transition"
                  >
                    <span>View Scorecard</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Sub-scores breakdown bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4 pt-4 border-t border-slate-800/80">
                <div className="bg-slate-800/40 p-2 rounded-xl border border-slate-800">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Skills</span>
                    <span className="font-semibold text-white">{item.skills_score}%</span>
                  </div>
                  <div className="w-full h-1 bg-slate-700 rounded-full mt-1.5 overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: `${item.skills_score}%` }} />
                  </div>
                </div>

                <div className="bg-slate-800/40 p-2 rounded-xl border border-slate-800">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Experience</span>
                    <span className="font-semibold text-white">{item.experience_score}%</span>
                  </div>
                  <div className="w-full h-1 bg-slate-700 rounded-full mt-1.5 overflow-hidden">
                    <div className="h-full bg-blue-500" style={{ width: `${item.experience_score}%` }} />
                  </div>
                </div>

                <div className="bg-slate-800/40 p-2 rounded-xl border border-slate-800">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Projects</span>
                    <span className="font-semibold text-white">{item.projects_score}%</span>
                  </div>
                  <div className="w-full h-1 bg-slate-700 rounded-full mt-1.5 overflow-hidden">
                    <div className="h-full bg-amber-500" style={{ width: `${item.projects_score}%` }} />
                  </div>
                </div>

                <div className="bg-slate-800/40 p-2 rounded-xl border border-slate-800">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Education</span>
                    <span className="font-semibold text-white">{item.education_score}%</span>
                  </div>
                  <div className="w-full h-1 bg-slate-700 rounded-full mt-1.5 overflow-hidden">
                    <div className="h-full bg-purple-500" style={{ width: `${item.education_score}%` }} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
