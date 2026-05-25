import React from 'react';

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

interface IResultsDashboardProps {
  evaluation: IEvaluation;
  generatedContent: IGeneratedContent;
  roadmap: IRoadmap;
  questions?: IQuestion[];
  round1Questions?: IQuestion[];
  disqualified?: boolean;
  round?: number;
}

const ResultsDashboard: React.FC<IResultsDashboardProps> = ({
  evaluation,
  generatedContent,
  roadmap,
  questions,
  round1Questions,
  disqualified = false,
  round = 1
}) => {
  const isAnswerCorrect = (correct: string, student: string): boolean => {
    return correct.toLowerCase().trim() === student.toLowerCase().trim();
  };

  const renderAnswerReview = (questionsToReview: IQuestion[], roundNum: number) => {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6">Round {roundNum} Answer Review</h2>
        <div className="space-y-6">
          {questionsToReview.map((q, index) => {
            const isCorrect = isAnswerCorrect(q.correct_answer, q.student_answer);
            return (
              <div key={index} className={`p-4 rounded-lg border-2 ${isCorrect ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'}`}>
                <div className="mb-3">
                  <h3 className="font-semibold text-lg">Question {index + 1}</h3>
                  <p className="text-gray-700 mt-2">{q.question}</p>
                </div>

                {q.options && q.options.length > 0 && (
                  <div className="mb-4 ml-4">
                    <p className="text-sm text-gray-600 mb-2">Options:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {q.options.map((option, idx) => (
                        <li key={idx} className={`text-sm ${option === q.correct_answer ? 'font-bold text-green-700' : ''}`}>
                          {option} {option === q.correct_answer && <span className="text-green-600">(Correct Answer)</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-white p-3 rounded border border-green-300">
                    <p className="font-semibold text-green-700">✓ Correct Answer:</p>
                    <p className="text-gray-800 mt-1">{q.correct_answer}</p>
                  </div>
                  <div className={`bg-white p-3 rounded border ${isCorrect ? 'border-green-300' : 'border-red-300'}`}>
                    <p className={`font-semibold ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                      {isCorrect ? '✓ Your Answer:' : '✗ Your Answer:'}
                    </p>
                    <p className="text-gray-800 mt-1">{q.student_answer || '(No answer provided)'}</p>
                  </div>
                </div>

                <div className="mt-3">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${isCorrect ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                    {isCorrect ? 'Correct' : 'Incorrect'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="mt-8 space-y-6">
      {/* Disqualification Message */}
      {disqualified && (
        <div className="p-6 bg-red-50 border-l-4 border-red-500 rounded-lg">
          <h2 className="text-2xl font-bold text-red-700 mb-2">Sorry! You didn't qualify for Round 2</h2>
          <p className="text-red-600 text-lg">
            You scored {evaluation.score}% on Round 1. You need to score at least 50% to proceed to Round 2.
          </p>
          <p className="text-red-600 mt-2">
            But don't worry! Here's a personalized learning path to help you master this topic.
          </p>
        </div>
      )}

      {/* Answer Review Section - Round 1 */}
      {round1Questions && round1Questions.length > 0 && round === 2 && renderAnswerReview(round1Questions, 1)}

      {/* Answer Review Section - Current Round */}
      {questions && questions.length > 0 && renderAnswerReview(questions, round)}

      {/* Evaluation Section */}
      <div className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-4">
          Evaluation Results
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-lg font-semibold">Score</p>

            <p
              className={`text-4xl font-bold ${
                evaluation.score < 50
                  ? 'text-red-500'
                  : 'text-green-500'
              }`}
            >
              {evaluation.score}
            </p>
          </div>

          <div>
            <p className="text-lg font-semibold">
              Learning Level
            </p>

            <p className="text-2xl">
              {evaluation.level}
            </p>
          </div>
        </div>

        <div className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div>
              <h3 className="text-lg font-semibold text-green-600">
                Strengths
              </h3>

              <ul className="list-disc list-inside mt-2">
                {evaluation.strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-red-600">
                Weak Areas
              </h3>

              <ul className="list-disc list-inside mt-2">
                {evaluation.weak_areas.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>

          </div>
        </div>
      </div>

      {/* Generated Content Section */}
      <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-md border border-blue-200">
        <h2 className="text-2xl font-bold mb-6 text-blue-900">
          {generatedContent.type === 'performance_analysis'
            ? 'Performance Analysis'
            : generatedContent.type === 'solution'
            ? 'Solution'
            : 'Advanced Insights & Challenges'}
        </h2>

        <div
          className="text-gray-800 leading-relaxed"
          dangerouslySetInnerHTML={{
            __html: generatedContent.content
              .replace(/^### (.*?)$/gm, '<h3 class="text-lg font-semibold text-blue-800 mt-4 mb-2">$1</h3>')
              .replace(/^## (.*?)$/gm, '<h2 class="text-xl font-bold text-blue-900 mt-6 mb-3">$1</h2>')
              .replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-900">$1</strong>')
              .replace(/^- (.*?)$/gm, '<li class="ml-4">$1</li>')
              .replace(/\n/g, '<br />')
          }}
        />
      </div>

      {/* Roadmap Section */}
      <div className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg shadow-md border border-emerald-200">
        <h2 className="text-2xl font-bold mb-6 text-emerald-900">
          {roadmap.title}
        </h2>

        <div
          className="text-gray-800 leading-relaxed"
          dangerouslySetInnerHTML={{
            __html: roadmap.content
              .replace(/^### (.*?)$/gm, '<h3 class="text-lg font-semibold text-emerald-800 mt-4 mb-2">$1</h3>')
              .replace(/^## (.*?)$/gm, '<h2 class="text-xl font-bold text-emerald-900 mt-6 mb-3">$1</h2>')
              .replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-900">$1</strong>')
              .replace(/^- (.*?)$/gm, '<li class="ml-4">$1</li>')
              .replace(/\n/g, '<br />')
          }}
        />
      </div>
    </div>
  );
};

export default ResultsDashboard;