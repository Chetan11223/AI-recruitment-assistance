import React, { useState, useEffect } from 'react';
import { X, Key, Cpu, Check, AlertCircle, Sparkles } from 'lucide-react';
import { getSettings, updateSettings } from '../api/client';

export default function SettingsModal({ isOpen, onClose, onSettingsUpdated }) {
  const [settings, setSettings] = useState(null);
  const [provider, setProvider] = useState('mock');
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [modelName, setModelName] = useState('');
  const [loading, setLoading] = useState(false);
  const [savedStatus, setSavedStatus] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      const data = await getSettings();
      setSettings(data);
      setProvider(data.active_provider || 'mock');
      setModelName(data.model_name || '');
    } catch (err) {
      console.error('Failed to load settings', err);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSavedStatus('');
    try {
      const payload = {
        active_provider: provider,
        model_name: modelName || undefined,
        gemini_api_key: geminiKey || undefined,
        openai_api_key: openaiKey || undefined,
        anthropic_api_key: anthropicKey || undefined,
        groq_api_key: groqKey || undefined,
      };
      await updateSettings(payload);
      setSavedStatus('Settings saved successfully!');
      if (onSettingsUpdated) onSettingsUpdated();
      setTimeout(() => {
        setSavedStatus('');
        onClose();
      }, 1200);
    } catch (err) {
      console.error('Failed to save settings', err);
      setSavedStatus('Error saving settings');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-800/50">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h3 className="text-lg font-semibold text-white">LLM Provider & Engine Settings</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSave} className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Active Intelligence Engine</label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'mock', name: 'Local Heuristic Engine', desc: 'Instant local structure-aware reasoning (No API key needed)' },
                { id: 'gemini', name: 'Google Gemini', desc: 'Gemini 2.5 Flash / Pro' },
                { id: 'openai', name: 'OpenAI', desc: 'GPT-4o / GPT-4o-mini' },
                { id: 'anthropic', name: 'Anthropic Claude', desc: 'Claude 3.5 Sonnet' },
                { id: 'groq', name: 'Groq Cloud', desc: 'Ultra-fast Llama 3.3 70B' },
              ].map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setProvider(p.id)}
                  className={`p-3 rounded-xl text-left border transition-all ${
                    provider === p.id
                      ? 'border-indigo-500 bg-indigo-500/10 text-white ring-1 ring-indigo-500'
                      : 'border-slate-800 bg-slate-800/40 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">{p.name}</span>
                    {provider === p.id && <Sparkles className="w-4 h-4 text-indigo-400" />}
                  </div>
                  <p className="text-xs text-slate-400 mt-1 leading-snug">{p.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {provider === 'gemini' && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Gemini API Key {settings?.has_gemini_key && <span className="text-emerald-400 font-normal">(Configured: {settings.gemini_masked})</span>}
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  placeholder="AIzaSy..."
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {provider === 'openai' && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                OpenAI API Key {settings?.has_openai_key && <span className="text-emerald-400 font-normal">(Configured: {settings.openai_masked})</span>}
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  placeholder="sk-..."
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {provider === 'anthropic' && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Anthropic API Key {settings?.has_anthropic_key && <span className="text-emerald-400 font-normal">(Configured: {settings.anthropic_masked})</span>}
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  placeholder="sk-ant-..."
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          {provider === 'groq' && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Groq API Key {settings?.has_groq_key && <span className="text-emerald-400 font-normal">(Configured: {settings.groq_masked})</span>}
              </label>
              <div className="relative">
                <Key className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  placeholder="gsk_..."
                  value={groqKey}
                  onChange={(e) => setGroqKey(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Model Name Override (Optional)</label>
            <input
              type="text"
              placeholder={provider === 'gemini' ? 'gemini-2.5-flash' : provider === 'openai' ? 'gpt-4o-mini' : 'Default model'}
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          {savedStatus && (
            <div className={`p-3 rounded-lg flex items-center space-x-2 text-sm ${savedStatus.includes('Error') ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}`}>
              {savedStatus.includes('Error') ? <AlertCircle className="w-4 h-4" /> : <Check className="w-4 h-4" />}
              <span>{savedStatus}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/25 transition disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
