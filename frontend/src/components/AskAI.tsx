import React, { useState } from 'react';
import { Lightbulb, Copy, X, Loader } from 'lucide-react';
import axios from 'axios';

interface AskAIProps {
  sessionUuid: string;
  questionIndex: number;
  questionText: string;
  onAIHelpUsed: (helpType: 'hint' | 'explanation') => void;
  disabled?: boolean;
}

export const AskAI: React.FC<AskAIProps> = ({
  sessionUuid,
  questionIndex,
  questionText,
  onAIHelpUsed,
  disabled = false
}) => {
  const [showPanel, setShowPanel] = useState(false);
  const [helpType, setHelpType] = useState<'hint' | 'explanation'>('hint');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiUsed, setAiUsed] = useState(false);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleAskAI = async () => {
    if (aiUsed) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/learning/ask-ai`, {
        session_uuid: sessionUuid,
        question_index: questionIndex,
        question_text: questionText,
        help_type: helpType
      });

      setContent(response.data.content);
      setAiUsed(true);
      onAIHelpUsed(helpType);
    } catch (error) {
      console.error('Failed to get AI help:', error);
      setContent('Failed to generate ' + helpType + '. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-6 space-y-3">
      {/* Ask AI Button */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setShowPanel(!showPanel)}
          disabled={disabled || aiUsed}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
            aiUsed
              ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-indigo-500/50'
          }`}
        >
          <Lightbulb size={18} />
          {aiUsed ? 'AI Help Used' : 'Ask AI'}
        </button>

        {aiUsed && (
          <span className="text-xs px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/50">
            with help
          </span>
        )}
      </div>

      {/* Mode Selection Panel */}
      {showPanel && !aiUsed && (
        <div className="border border-slate-700 rounded-lg p-4 bg-slate-800/50">
          <div className="space-y-3">
            <label className="text-sm text-slate-300">How would you like help?</label>

            <div className="space-y-2">
              <label className="flex items-center gap-3 p-2 rounded cursor-pointer hover:bg-slate-700/50 transition-colors">
                <input
                  type="radio"
                  checked={helpType === 'hint'}
                  onChange={() => setHelpType('hint')}
                  className="accent-indigo-500"
                />
                <span className="text-sm text-slate-200">Hint (guidance without answer)</span>
              </label>

              <label className="flex items-center gap-3 p-2 rounded cursor-pointer hover:bg-slate-700/50 transition-colors">
                <input
                  type="radio"
                  checked={helpType === 'explanation'}
                  onChange={() => setHelpType('explanation')}
                  className="accent-indigo-500"
                />
                <span className="text-sm text-slate-200">Full Explanation</span>
              </label>
            </div>

            <button
              onClick={handleAskAI}
              disabled={loading}
              className="w-full mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
            >
              {loading && <Loader size={16} className="animate-spin" />}
              {loading ? 'Generating...' : 'Get ' + (helpType === 'hint' ? 'Hint' : 'Explanation')}
            </button>
          </div>
        </div>
      )}

      {/* AI Response Panel */}
      {content && (
        <div className="border border-indigo-500/30 rounded-lg p-4 bg-indigo-500/5">
          <div className="flex items-start justify-between mb-3">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wide">
              {helpType === 'hint' ? '💡 Hint' : '📚 Explanation'}
            </span>
            <button
              onClick={() => {
                setContent('');
                setShowPanel(false);
              }}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X size={16} />
            </button>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{content}</p>

          <button
            onClick={() => {
              navigator.clipboard.writeText(content);
            }}
            className="mt-3 flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <Copy size={14} />
            Copy
          </button>
        </div>
      )}
    </div>
  );
};
