import React, { useState } from 'react';
import { 
  ChevronRight, ChevronDown, Folder, FileText, CheckCircle, 
  ExternalLink, Sparkles, Search, Layers, User, Calendar, Tag
} from 'lucide-react';

function TreeNode({ node, level = 0, onSelectCitation, searchFilter }) {
  const [isOpen, setIsOpen] = useState(level < 2); // default open up to level 2

  const hasChildren = node.children && node.children.length > 0;
  
  // Highlight if matches search filter
  const matchesSearch = searchFilter && (
    node.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
    node.summary.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (node.key_entities && node.key_entities.some(e => e.toLowerCase().includes(searchFilter.toLowerCase())))
  );

  const getNodeColor = () => {
    if (node.node_type === 'document') return 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300';
    if (node.node_type === 'section') return 'bg-purple-500/10 border-purple-500/30 text-purple-300';
    if (node.node_type === 'entry') return 'bg-blue-500/10 border-blue-500/30 text-blue-300';
    return 'bg-slate-800/80 border-slate-700/60 text-slate-300';
  };

  const getNodeBadge = () => {
    if (node.node_type === 'document') return 'DOCUMENT ROOT';
    if (node.node_type === 'section') return 'SECTION';
    if (node.node_type === 'entry') return 'ENTRY';
    return 'SUB-ENTRY';
  };

  return (
    <div className={`my-1.5 transition-all ${level > 0 ? 'ml-4 sm:ml-6 pl-2 border-l border-slate-800' : ''}`}>
      <div 
        className={`p-3 rounded-xl border transition-all ${getNodeColor()} ${
          matchesSearch ? 'ring-2 ring-amber-400/80 bg-amber-500/10' : ''
        }`}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start space-x-2 flex-1 min-w-0">
            {hasChildren ? (
              <button 
                onClick={() => setIsOpen(!isOpen)} 
                className="mt-0.5 text-slate-400 hover:text-white p-0.5 rounded hover:bg-slate-700/50 transition"
              >
                {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
            ) : (
              <span className="w-4 h-4 mt-0.5 flex items-center justify-center text-slate-600">•</span>
            )}

            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60">
                  {getNodeBadge()}
                </span>
                <h4 className="text-sm font-semibold text-white truncate">{node.title}</h4>
              </div>

              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">{node.summary}</p>

              {node.key_entities && node.key_entities.length > 0 && (
                <div className="flex items-center flex-wrap gap-1 mt-2">
                  <Tag className="w-3 h-3 text-slate-500 mr-1" />
                  {node.key_entities.map((entity, idx) => (
                    <span 
                      key={idx} 
                      className="text-[10px] bg-slate-800/90 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded-md font-mono"
                    >
                      {entity}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {node.citation && (
            <button
              onClick={() => onSelectCitation(node.citation, node.title)}
              className="text-[11px] flex items-center space-x-1 text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 px-2 py-1 rounded-lg transition whitespace-nowrap"
              title="Inspect grounded raw text & page location"
            >
              <ExternalLink className="w-3 h-3" />
              <span>Page {node.citation.page_number}</span>
            </button>
          )}
        </div>
      </div>

      {hasChildren && isOpen && (
        <div className="mt-1">
          {node.children.map((child) => (
            <TreeNode 
              key={child.node_id} 
              node={child} 
              level={level + 1} 
              onSelectCitation={onSelectCitation}
              searchFilter={searchFilter}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function PageIndexTreeVisualizer({ candidates, selectedCandidateId, onSelectCandidate }) {
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedCitation, setSelectedCitation] = useState(null);

  const activeCandidate = candidates.find(c => c.candidate_id === selectedCandidateId) || candidates[0];

  if (!activeCandidate) {
    return (
      <div className="p-12 text-center text-slate-400 bg-slate-900/50 rounded-2xl border border-slate-800">
        <Layers className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-base font-medium text-slate-300">No candidate resumes available</p>
        <p className="text-xs text-slate-500 mt-1">Please load sample data or upload resumes first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Controls: Candidate Selector & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center space-x-3 overflow-x-auto pb-1 md:pb-0">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">Candidate:</span>
          {candidates.map((c) => (
            <button
              key={c.candidate_id}
              onClick={() => onSelectCandidate(c.candidate_id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center space-x-1.5 whitespace-nowrap ${
                activeCandidate.candidate_id === c.candidate_id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
              }`}
            >
              <User className="w-3.5 h-3.5" />
              <span>{c.candidate_name}</span>
              <span className="text-[10px] opacity-75">({c.overall_yoe}y)</span>
            </button>
          ))}
        </div>

        {/* Tree Search / Concept Filter */}
        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search entities (e.g., Kafka, PyTorch)..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Main Grid: Tree Explorer + Citation Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tree Column */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">Hierarchical PageIndex Tree</h3>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Vectorless Index
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Structured node table of contents navigated by the LLM reasoning agent
              </p>
            </div>
            <span className="text-xs text-slate-500 font-mono">
              {activeCandidate.index_tree?.children?.length || 0} Sections
            </span>
          </div>

          {activeCandidate.index_tree ? (
            <div className="overflow-y-auto max-h-[700px] pr-2">
              <TreeNode 
                node={activeCandidate.index_tree} 
                level={0} 
                onSelectCitation={(cit, title) => setSelectedCitation({ ...cit, nodeTitle: title })}
                searchFilter={searchFilter}
              />
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-8 text-center">No PageIndex tree generated for this candidate.</p>
          )}
        </div>

        {/* Citation & Grounding Inspector Column */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col">
          <div className="border-b border-slate-800 pb-3 mb-4">
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              <span>Grounded Evidence Inspector</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Click any node's "Page" badge to inspect raw text excerpts & exact offsets
            </p>
          </div>

          {selectedCitation ? (
            <div className="space-y-4 flex-1 overflow-y-auto">
              <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-3.5">
                <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Cited Node</span>
                <h4 className="text-sm font-semibold text-white mt-1">{selectedCitation.nodeTitle}</h4>
                <div className="flex items-center space-x-3 text-xs text-slate-400 mt-2">
                  <span>📄 Page {selectedCitation.page_number}</span>
                  <span>📍 Char {selectedCitation.char_start} – {selectedCitation.char_end}</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Raw Verified Excerpt:</span>
                <div className="mt-1.5 p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {selectedCitation.raw_text}
                </div>
              </div>

              <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50">
                <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold">
                  <CheckCircle className="w-4 h-4" />
                  <span>Grounding Contract Verified</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Every claim made by the scoring agent is traceable to exact character spans in the original resume document.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
              <ExternalLink className="w-8 h-8 text-slate-600 mb-2" />
              <p className="text-xs">Select any PageIndex node on the left to inspect verified resume excerpts.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
