import React, { useState } from 'react';
import { 
  Upload, FileText, Briefcase, Trash2, Plus, Check, 
  AlertCircle, Sparkles, User, Calendar, Tag
} from 'lucide-react';
import { uploadResumes, deleteResume, createJob, deleteJob } from '../api/client';

export default function ManageData({ 
  candidates, 
  jobs, 
  onRefreshData, 
  selectedJobId, 
  onSelectJob 
}) {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  
  // New Job Form State
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [jobTitle, setJobTitle] = useState('');
  const [jobCompany, setJobCompany] = useState('');
  const [jobMinYoe, setJobMinYoe] = useState(4.0);
  const [jobRawText, setJobRawText] = useState('');
  const [creatingJobLoading, setCreatingJobLoading] = useState(false);

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    setUploading(true);
    setUploadStatus('');
    try {
      await uploadResumes(formData);
      setUploadStatus(`Successfully parsed ${files.length} resume(s) into PageIndex trees!`);
      onRefreshData();
      setTimeout(() => setUploadStatus(''), 4000);
    } catch (err) {
      console.error('Upload failed', err);
      setUploadStatus('Failed to upload/parse files. Please check formats (PDF/DOCX/TXT).');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteResume = async (candId) => {
    if (confirm('Are you sure you want to delete this candidate profile?')) {
      try {
        await deleteResume(candId);
        onRefreshData();
      } catch (err) {
        console.error('Delete candidate error', err);
      }
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!jobTitle.trim() || !jobRawText.trim()) return;

    setCreatingJobLoading(true);
    try {
      const newJob = await createJob({
        title: jobTitle,
        company: jobCompany || 'Tech Company',
        min_yoe: parseFloat(jobMinYoe) || 3.0,
        raw_text: jobRawText
      });
      setIsCreatingJob(false);
      setJobTitle('');
      setJobCompany('');
      setJobRawText('');
      onRefreshData();
      onSelectJob(newJob.job_id);
    } catch (err) {
      console.error('Create job error', err);
    } finally {
      setCreatingJobLoading(false);
    }
  };

  const handleDeleteJob = async (jobId) => {
    if (confirm('Are you sure you want to delete this Job Description?')) {
      try {
        await deleteJob(jobId);
        onRefreshData();
      } catch (err) {
        console.error('Delete job error', err);
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Upload Resumes Section */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Upload className="w-5 h-5 text-indigo-400" />
              <span>Resume Ingestion & Vectorless PageIndex Builder</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Upload PDF, DOCX, or TXT resumes. The system will automatically segment sections and build hierarchical reasoning trees.
            </p>
          </div>
        </div>

        {/* Upload Dropzone */}
        <label className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer bg-slate-950/40 hover:bg-indigo-500/5 transition group">
          <div className="w-12 h-12 rounded-2xl bg-slate-800 group-hover:bg-indigo-600 flex items-center justify-center text-slate-400 group-hover:text-white transition shadow-lg mb-3">
            <Upload className="w-6 h-6" />
          </div>
          <span className="text-sm font-semibold text-white">
            {uploading ? 'Parsing & Indexing...' : 'Click to select or drag & drop resumes'}
          </span>
          <span className="text-xs text-slate-500 mt-1">Supports PDF, DOCX, and Plain Text resumes</span>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>

        {uploadStatus && (
          <div className={`mt-4 p-3 rounded-xl flex items-center space-x-2 text-xs ${
            uploadStatus.includes('Failed') ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
          }`}>
            {uploadStatus.includes('Failed') ? <AlertCircle className="w-4 h-4" /> : <Check className="w-4 h-4" />}
            <span>{uploadStatus}</span>
          </div>
        )}

        {/* Candidates List */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Active Candidate Repository ({candidates.length})
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {candidates.map((cand) => (
              <div key={cand.candidate_id} className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-4 flex items-start justify-between">
                <div className="space-y-1 min-w-0 flex-1 pr-2">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4 text-indigo-400 shrink-0" />
                    <h4 className="text-sm font-bold text-white truncate">{cand.candidate_name}</h4>
                    <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded uppercase font-mono">
                      {cand.file_type}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-xs text-slate-400">
                    <span>{cand.overall_yoe} Years Experience</span>
                    {cand.contact_email && <span className="truncate">{cand.contact_email}</span>}
                  </div>
                  {cand.top_skills && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {cand.top_skills.slice(0, 5).map((s, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-900 text-slate-300 border border-slate-700 px-1.5 py-0.5 rounded">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleDeleteResume(cand.candidate_id)}
                  className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-700/50 transition"
                  title="Delete Candidate"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Job Descriptions Section */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Briefcase className="w-5 h-5 text-indigo-400" />
              <span>Job Descriptions & Target Rubrics</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Define target technical roles against which candidates will be scored and ranked.
            </p>
          </div>

          <button
            onClick={() => setIsCreatingJob(!isCreatingJob)}
            className="flex items-center space-x-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-2 rounded-xl transition shadow"
          >
            <Plus className="w-4 h-4" />
            <span>{isCreatingJob ? 'Close Form' : 'New Job Description'}</span>
          </button>
        </div>

        {/* Create Job Form */}
        {isCreatingJob && (
          <form onSubmit={handleCreateJob} className="mb-6 bg-slate-950 p-5 rounded-xl border border-slate-700 space-y-4 animate-in fade-in">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-400 mb-1">Job Title</label>
                <input
                  type="text"
                  placeholder="e.g., Staff Backend Engineer (Distributed Systems)"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Min YoE</label>
                <input
                  type="number"
                  step="0.5"
                  value={jobMinYoe}
                  onChange={(e) => setJobMinYoe(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Company / Division (Optional)</label>
              <input
                type="text"
                placeholder="e.g., Tech Innovations Inc."
                value={jobCompany}
                onChange={(e) => setJobCompany(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Job Requirements & Description (Text / Bullets)</label>
              <textarea
                rows={5}
                placeholder="Paste full Job Description text here including responsibilities and required skills..."
                value={jobRawText}
                onChange={(e) => setJobRawText(e.target.value)}
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs text-white focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setIsCreatingJob(false)}
                className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creatingJobLoading}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow transition disabled:opacity-50"
              >
                {creatingJobLoading ? 'Creating...' : 'Save Job Description'}
              </button>
            </div>
          </form>
        )}

        {/* Existing JDs List */}
        <div className="space-y-3">
          {jobs.map((job) => {
            const isSelected = job.job_id === selectedJobId;
            return (
              <div
                key={job.job_id}
                className={`p-4 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-500/10 ring-1 ring-indigo-500'
                    : 'border-slate-700/60 bg-slate-800/40 hover:border-slate-600'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white">{job.title}</h4>
                    <span className="text-xs text-slate-400">({job.company})</span>
                    {isSelected && (
                      <span className="text-[10px] bg-indigo-500 text-white px-2 py-0.5 rounded-full font-bold">
                        ACTIVE TARGET
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400">Min {job.min_yoe} Years Required</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {job.must_have_skills.map((s, idx) => (
                      <span key={idx} className="text-[10px] bg-slate-900 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2 self-end md:self-center">
                  {!isSelected && (
                    <button
                      onClick={() => onSelectJob(job.job_id)}
                      className="text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 transition"
                    >
                      Set as Target
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteJob(job.job_id)}
                    className="text-slate-500 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-700/50 transition"
                    title="Delete Job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
