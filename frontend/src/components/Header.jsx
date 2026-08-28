import React from 'react';
import { 
  Sparkles, Layers, Sliders, Database, 
  Trophy, GitBranch, MessageSquare, Briefcase
} from 'lucide-react';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  onOpenSettings, 
  settings, 
  onPreloadSamples, 
  preloading,
  candidateCount,
  jobCount
}) {
  const getProviderBadge = () => {
    const provider = settings?.active_provider || 'mock';
    if (provider === 'gemini') return { name: 'Gemini 2.5 Flash', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30' };
    if (provider === 'openai') return { name: 'OpenAI GPT-4o', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' };
    if (provider === 'anthropic') return { name: 'Claude 3.5 Sonnet', color: 'bg-amber-500/10 text-amber-400 border-amber-500/30' };
    if (provider === 'groq') return { name: 'Groq Llama 3.3', color: 'bg-orange-500/10 text-orange-400 border-orange-500/30' };
    return { name: 'Local Heuristic Engine', color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30' };
  };

  const badge = getProviderBadge();

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">Resume Intelligence</span>
                <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  PageIndex + Agentic RAG
                </span>
              </div>
              <p className="text-xs text-slate-400">Vectorless Structure-Aware Resume Screening & Ranking</p>
            </div>
          </div>

          {/* Quick Actions & Status */}
          <div className="flex items-center space-x-3">
            {/* Stats Badges */}
            <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50">
              <span>{candidateCount} Resumes</span>
              <span className="text-slate-600">•</span>
              <span>{jobCount} JDs</span>
            </div>

            {/* Provider Badge */}
            <div className={`hidden sm:flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full border ${badge.color}`}>
              <Sparkles className="w-3.5 h-3.5" />
              <span>{badge.name}</span>
            </div>

            {/* Preload Samples Button */}
            <button
              onClick={onPreloadSamples}
              disabled={preloading}
              className="flex items-center space-x-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition disabled:opacity-50"
              title="Preload 5 realistic sample resumes and 2 technical job descriptions"
            >
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              <span>{preloading ? 'Loading...' : 'Load Sample Data'}</span>
            </button>

            {/* Settings Button */}
            <button
              onClick={onOpenSettings}
              className="flex items-center space-x-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 transition"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Settings</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 border-t border-slate-800/80 -mb-px overflow-x-auto">
          {[
            { id: 'leaderboard', label: 'Ranked Leaderboard', icon: Trophy },
            { id: 'tree_explorer', label: 'PageIndex Tree Visualizer', icon: GitBranch },
            { id: 'chat', label: 'Recruiter Agent Q&A', icon: MessageSquare },
            { id: 'jobs_resumes', label: 'Manage Resumes & JDs', icon: Briefcase },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-indigo-500 text-indigo-400 bg-indigo-500/5'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
