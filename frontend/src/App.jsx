import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SettingsModal from './components/SettingsModal';
import Leaderboard from './components/Leaderboard';
import PageIndexTreeVisualizer from './components/PageIndexTreeVisualizer';
import RecruiterChat from './components/RecruiterChat';
import ManageData from './components/ManageData';
import ScorecardModal from './components/ScorecardModal';
import { 
  getResumes, getJobs, getSettings, getRanking, 
  rankCandidates, preloadSamples 
} from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('leaderboard');
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null);
  const [ranking, setRanking] = useState(null);
  const [rankingInProgress, setRankingInProgress] = useState(false);
  const [settings, setSettings] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [preloading, setPreloading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Scorecard Modal
  const [scorecardState, setScorecardState] = useState({
    isOpen: false,
    candidate: null,
    job: null
  });

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    setInitialLoading(true);
    try {
      await refreshAllData();
    } catch (err) {
      console.error('Failed to initialize app', err);
    } finally {
      setInitialLoading(false);
    }
  };

  const refreshAllData = async () => {
    try {
      const [resumesData, jobsData, settingsData] = await Promise.all([
        getResumes(),
        getJobs(),
        getSettings()
      ]);

      setCandidates(resumesData);
      setJobs(jobsData);
      setSettings(settingsData);

      let currentJobId = selectedJobId;
      if (!currentJobId && jobsData.length > 0) {
        currentJobId = jobsData[0].job_id;
        setSelectedJobId(currentJobId);
      }

      if (!selectedCandidateId && resumesData.length > 0) {
        setSelectedCandidateId(resumesData[0].candidate_id);
      }

      if (currentJobId) {
        loadRanking(currentJobId);
      }
    } catch (err) {
      console.error('Data refresh error', err);
    }
  };

  const loadRanking = async (jobId) => {
    if (!jobId) return;
    try {
      const rankData = await getRanking(jobId);
      setRanking(rankData);
    } catch (err) {
      console.error('Ranking load error', err);
    }
  };

  const handleRunRanking = async (jobId) => {
    const targetJobId = jobId || selectedJobId;
    if (!targetJobId) return;

    setRankingInProgress(true);
    try {
      const result = await rankCandidates(targetJobId);
      setRanking(result);
    } catch (err) {
      console.error('Ranking run error', err);
    } finally {
      setRankingInProgress(false);
    }
  };

  const handleSelectJob = (jobId) => {
    setSelectedJobId(jobId);
    loadRanking(jobId);
  };

  const handlePreloadSamples = async () => {
    setPreloading(true);
    try {
      await preloadSamples();
      await refreshAllData();
    } catch (err) {
      console.error('Preload samples error', err);
    } finally {
      setPreloading(false);
    }
  };

  const handleOpenScorecard = (rankItem, job) => {
    const cand = candidates.find(c => c.candidate_id === rankItem.candidate_id);
    if (cand) {
      setScorecardState({
        isOpen: true,
        candidate: cand,
        job: job
      });
    }
  };

  const handleCloseScorecard = () => {
    setScorecardState({ isOpen: false, candidate: null, job: null });
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
        <div className="animate-spin w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full mb-4" />
        <h2 className="text-base font-bold text-white">Initializing PageIndex & Agentic RAG System...</h2>
        <p className="text-xs text-slate-500 mt-1">Connecting to FastAPI backend & loading knowledge trees</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Top Header & Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSettings={() => setIsSettingsOpen(true)}
        settings={settings}
        onPreloadSamples={handlePreloadSamples}
        preloading={preloading}
        candidateCount={candidates.length}
        jobCount={jobs.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'leaderboard' && (
          <Leaderboard
            jobs={jobs}
            selectedJobId={selectedJobId}
            onSelectJob={handleSelectJob}
            candidates={candidates}
            ranking={ranking}
            onRunRanking={handleRunRanking}
            rankingInProgress={rankingInProgress}
            onOpenScorecard={handleOpenScorecard}
          />
        )}

        {activeTab === 'tree_explorer' && (
          <PageIndexTreeVisualizer
            candidates={candidates}
            selectedCandidateId={selectedCandidateId}
            onSelectCandidate={setSelectedCandidateId}
          />
        )}

        {activeTab === 'chat' && (
          <RecruiterChat
            selectedJobId={selectedJobId}
            candidates={candidates}
            jobs={jobs}
          />
        )}

        {activeTab === 'jobs_resumes' && (
          <ManageData
            candidates={candidates}
            jobs={jobs}
            onRefreshData={refreshAllData}
            selectedJobId={selectedJobId}
            onSelectJob={handleSelectJob}
          />
        )}
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSettingsUpdated={refreshAllData}
      />

      {/* Grounded Scorecard & Citation Modal */}
      <ScorecardModal
        isOpen={scorecardState.isOpen}
        onClose={handleCloseScorecard}
        candidate={scorecardState.candidate}
        job={scorecardState.job}
      />
    </div>
  );
}
