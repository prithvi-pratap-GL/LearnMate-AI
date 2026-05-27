import React from 'react';
import { Outlet } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';

const Layout: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-[rgb(var(--background))] text-[rgb(var(--foreground))] transition-colors duration-300">
      <nav className="bg-[rgb(var(--card))] shadow-md border-b border-[rgb(var(--border))]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <a href="/" className="text-2xl font-bold text-[rgb(var(--primary))]">
              LearnMate AI
            </a>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-[rgb(var(--secondary))] hover:bg-[rgb(var(--muted))] transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l-2.121-2.121a1 1 0 00-1.414 0l-2.121 2.121a1 1 0 001.414 1.414L9 13.414l1.464 1.465a1 1 0 001.414-1.414zm2.121-10.607a1 1 0 010 1.414l-1.414 1.414a1 1 0 11-1.414-1.414l1.414-1.414a1 1 0 011.414 0zM3.464 4.464a1 1 0 000 1.414L4.878 7.293a1 1 0 001.414-1.414L4.878 3.05a1 1 0 00-1.414 0zm10.607 9.172a1 1 0 010 1.414l-1.414 1.414a1 1 0 11-1.414-1.414l1.414-1.414a1 1 0 011.414 0zM5 8a1 1 0 011-1h2a1 1 0 110 2H6a1 1 0 01-1-1zm10 0a1 1 0 011-1h2a1 1 0 110 2h-2a1 1 0 01-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
