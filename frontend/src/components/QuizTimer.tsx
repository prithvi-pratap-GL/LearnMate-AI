import React, { useState, useEffect } from 'react';
import { Clock, RotateCcw } from 'lucide-react';

interface QuizTimerProps {
  onQuestionTimeUpdate: () => void;
  enabled: boolean;
}

export const QuizTimer: React.FC<QuizTimerProps> = ({ onQuestionTimeUpdate, enabled }) => {
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [questionSeconds, setQuestionSeconds] = useState(0);
  const [timerEnabled, setTimerEnabled] = useState(enabled);

  useEffect(() => {
    if (!timerEnabled) return;

    const interval = setInterval(() => {
      setTotalSeconds(prev => prev + 1);
      setQuestionSeconds(prev => prev + 1);
      onQuestionTimeUpdate();
    }, 1000);

    return () => clearInterval(interval);
  }, [timerEnabled, questionSeconds, onQuestionTimeUpdate]);

  const formatTime = (seconds: number) => {
    if (seconds < 3600) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleReset = () => {
    setQuestionSeconds(0);
  };

  return (
    <div className="fixed top-6 right-6 bg-slate-900/80 backdrop-blur-sm border border-slate-700 rounded-lg p-4 z-50">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Clock size={18} className="text-indigo-400" />
          <span className="text-sm font-mono text-slate-300">Q: {formatTime(questionSeconds)}</span>
        </div>

        <div className="w-px h-6 bg-slate-700" />

        <div className="flex items-center gap-2">
          <Clock size={18} className="text-green-400" />
          <span className="text-sm font-mono text-slate-300">Total: {formatTime(totalSeconds)}</span>
        </div>

        <div className="w-px h-6 bg-slate-700" />

        <button
          onClick={() => setTimerEnabled(!timerEnabled)}
          className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
            timerEnabled
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
              : 'bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30'
          }`}
        >
          {timerEnabled ? 'Pause' : 'Start'}
        </button>

        <button
          onClick={handleReset}
          disabled={!timerEnabled}
          className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Reset question timer"
        >
          <RotateCcw size={16} />
        </button>
      </div>
    </div>
  );
};
