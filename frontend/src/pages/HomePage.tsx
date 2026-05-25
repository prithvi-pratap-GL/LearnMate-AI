import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 text-gray-800">
      <h1 className="text-5xl font-bold mb-4">Welcome to LearnMate AI</h1>
      <p className="text-xl mb-8">Your personalized AI learning coach.</p>
      <Link to="/quiz">
        <button className="bg-purple-600 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition duration-300">
          Start Learning
        </button>
      </Link>
    </div>
  );
};

export default HomePage;
