import React, { useState } from 'react';
import axios from 'axios';
import ResultsDashboard from '../components/ResultsDashboard';

// --- Interfaces ---
interface IQuestion {
  question: string;
  correct_answer: string;
  student_answer: string;
  options?: string[];
}

interface IEvaluation {
  score: number;
  strengths: string[];
  weak_areas: string[];
  level: string;
}

interface IGeneratedContent {
  type: string;
  content: string;
}

interface IRoadmap {
  title: string;
  content: string;
}

interface IAnalysisResult {
  evaluation?: IEvaluation;
  round_2_evaluation?: IEvaluation;
  generated_content: IGeneratedContent;
  roadmap: IRoadmap;
  questions?: IQuestion[];
  round_1_score?: number;
  status: string;
  round: number;
  can_proceed_to_round_2?: boolean;
}

// --- Component ---
const QuizPage: React.FC = () => {
  const [studentName, setStudentName] = useState('');
  const [topic, setTopic] = useState('');
  const [currentRound, setCurrentRound] = useState(0); // 0 = input, 1 = round 1, 2 = round 2
  const [questions, setQuestions] = useState<IQuestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IAnalysisResult | null>(null);
  const [round1Evaluation, setRound1Evaluation] = useState<IEvaluation | null>(null);
  const [round1Score, setRound1Score] = useState<number | null>(null);

  const handleGenerateRound1Questions = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }
    if (!studentName.trim()) {
      setError('Please enter your name');
      return;
    }
    setGeneratingQuestions(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/api/generate-questions', {
        topic
      });
      const generatedQuestions = response.data.questions.map((q: any) => ({
        question: q.question,
        correct_answer: q.correct_answer,
        student_answer: '',
        options: q.options || []
      }));
      setQuestions(generatedQuestions);
      setCurrentRound(1);
    } catch (err) {
      setError('Failed to generate questions. Please try again.');
      console.error('Error generating questions', err);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleQuestionChange = (index: number, field: keyof IQuestion, value: string) => {
    const newQuestions = [...questions];
    newQuestions[index][field] = value;
    setQuestions(newQuestions);
  };

  const handleSubmitRound1 = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      student_name: studentName,
      topic,
      questions,
    };

    try {
      const response = await axios.post('http://localhost:8000/api/submit-round-1', payload);
      const data = response.data;

      if (data.can_proceed_to_round_2) {
        // User passed Round 1, prepare for Round 2
        setRound1Evaluation(data.evaluation);
        setRound1Score(data.score);
        await generateRound2Questions();
      } else {
        // User failed Round 1, show results
        setResult({
          status: data.status,
          round: 1,
          evaluation: data.evaluation,
          generated_content: data.generated_content,
          roadmap: data.roadmap,
          questions,
        });
        setCurrentRound(0);
      }
    } catch (err) {
      setError('Failed to submit Round 1. Please try again.');
      console.error('Error submitting Round 1', err);
    } finally {
      setLoading(false);
    }
  };

  const generateRound2Questions = async () => {
    setGeneratingQuestions(true);
    try {
      const response = await axios.post('http://localhost:8000/api/generate-round-2-questions', {
        topic
      });
      const generatedQuestions = response.data.questions.map((q: any) => ({
        question: q.question,
        correct_answer: q.correct_answer,
        student_answer: '',
        options: q.options || []
      }));
      setQuestions(generatedQuestions);
      setCurrentRound(2);
    } catch (err) {
      setError('Failed to generate Round 2 questions. Please try again.');
      console.error('Error generating Round 2 questions', err);
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleSubmitRound2 = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      student_name: studentName,
      topic,
      questions,
      round_1_score: round1Score || 0,
      round_1_evaluation: round1Evaluation || {}
    };

    try {
      const response = await axios.post('http://localhost:8000/api/submit-round-2', payload);
      setResult({
        status: response.data.status,
        round: 2,
        round_1_score: response.data.round_1_score,
        round_2_evaluation: response.data.round_2_evaluation,
        generated_content: response.data.generated_content,
        roadmap: response.data.roadmap,
        questions,
      });
      setCurrentRound(0);
    } catch (err) {
      setError('Failed to submit Round 2. Please try again.');
      console.error('Error submitting Round 2', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setStudentName('');
    setTopic('');
    setQuestions([]);
    setCurrentRound(0);
    setResult(null);
    setError(null);
    setRound1Evaluation(null);
    setRound1Score(null);
  };

  // Initial input screen
  if (currentRound === 0 && !result) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">Learning Assessment</h1>
        <div className="p-6 bg-white rounded-lg shadow-md space-y-6 max-w-md mx-auto">
          <div>
            <label htmlFor="studentName" className="block text-sm font-medium text-gray-700">Student Name</label>
            <input
              type="text"
              id="studentName"
              value={studentName}
              onChange={(e) => setStudentName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              placeholder="Enter your name"
              required
            />
          </div>
          <div>
            <label htmlFor="topic" className="block text-sm font-medium text-gray-700">Topic</label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              placeholder="Enter topic to learn about"
              required
            />
          </div>
          <button
            type="button"
            onClick={handleGenerateRound1Questions}
            className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition duration-300 disabled:bg-gray-400"
            disabled={generatingQuestions || !topic.trim() || !studentName.trim()}
          >
            {generatingQuestions ? 'Generating Round 1...' : 'Start Round 1 (5 Questions)'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg shadow-md max-w-md mx-auto">
            <p>{error}</p>
          </div>
        )}
      </div>
    );
  }

  // Round 1 or Round 2 quiz screens
  if ((currentRound === 1 || currentRound === 2) && !result) {
    return (
      <div className="container mx-auto p-4">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Round {currentRound}</h1>
          <span className="text-sm font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded">{currentRound === 1 ? 'Beginner Level' : 'Advanced Level'}</span>
        </div>

        <form onSubmit={currentRound === 1 ? handleSubmitRound1 : handleSubmitRound2} className="space-y-6">
          {questions.map((q, index) => (
            <div key={index} className="p-6 bg-white rounded-lg shadow-md space-y-4">
              <h2 className="text-xl font-semibold">Question {index + 1}</h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 font-bold">Question</label>
                <p className="mt-2 text-gray-800">{q.question}</p>
              </div>

              {q.options && q.options.length > 0 ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Your Answer</label>
                  <div className="space-y-2">
                    {q.options.map((option, optIndex) => (
                      <div key={optIndex} className="flex items-center">
                        <input
                          type="radio"
                          id={`q${index}_opt${optIndex}`}
                          name={`question${index}`}
                          value={option}
                          checked={q.student_answer === option}
                          onChange={(e) => handleQuestionChange(index, 'student_answer', e.target.value)}
                          className="h-4 w-4 text-purple-600 focus:ring-purple-500"
                          required
                        />
                        <label htmlFor={`q${index}_opt${optIndex}`} className="ml-3 block text-sm text-gray-700 cursor-pointer">
                          {option}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Your Answer</label>
                  <textarea
                    value={q.student_answer}
                    onChange={(e) => handleQuestionChange(index, 'student_answer', e.target.value)}
                    placeholder="Enter your answer here..."
                    className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    rows={4}
                    required
                  />
                </div>
              )}
            </div>
          ))}

          <div className="flex gap-4">
            <button
              type="button"
              onClick={handleReset}
              className="bg-gray-500 text-white font-bold py-2 px-4 rounded hover:bg-gray-600 transition duration-300"
            >
              Exit
            </button>
            <button
              type="submit"
              className="flex-1 bg-purple-600 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition duration-300 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? `Analyzing Round ${currentRound}...` : `Submit Round ${currentRound}`}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg shadow-md">
            <p>{error}</p>
          </div>
        )}
      </div>
    );
  }

  // Results screen
  if (result) {
    return (
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">Analysis for {studentName}</h1>
        {result.round === 1 && (
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded">
            <p className="text-blue-700 font-semibold">Round 1 Score: {result.evaluation?.score}%</p>
            <p className="text-blue-600 text-sm">You scored below 50%, so here's a tailored beginner learning path.</p>
          </div>
        )}
        {result.round === 2 && (
          <div className="mb-4 p-4 bg-green-50 border-l-4 border-green-400 rounded">
            <p className="text-green-700 font-semibold">Round 1 Score: {result.round_1_score}% | Round 2 Complete</p>
            <p className="text-green-600 text-sm">Great job! Here's your comprehensive analysis and learning roadmap.</p>
          </div>
        )}
        <ResultsDashboard
          evaluation={result.round === 2 ? result.round_2_evaluation : result.evaluation}
          generatedContent={result.generated_content}
          roadmap={result.roadmap}
          questions={result.questions}
          round={result.round}
          disqualified={result.round === 1 && !result.can_proceed_to_round_2}
        />
        <button
          onClick={handleReset}
          className="mt-8 bg-purple-600 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition duration-300"
        >
          Start New Assessment
        </button>
      </div>
    );
  }

  return null;
};

export default QuizPage;
