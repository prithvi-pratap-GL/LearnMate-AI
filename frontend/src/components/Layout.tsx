import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 backdrop-blur-md border-b border-[var(--border)] bg-[rgba(10,10,15,0.7)]">
        <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <div className="w-8 h-8 bg-[var(--accent)] rounded flex items-center justify-center">
              <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24"><path d="M13 2L4.09 12.26c-.36.44-.55.66-.55.88 0 .2.08.39.21.53.15.16.36.33.88.33H12l-1 8 8.91-10.26c.36-.44.55-.66.55-.88a.72.72 0 0 0-.21-.53c-.15-.16-.36-.33-.88-.33H13l1-8z"/></svg>
            </div>
            LearnMate AI
          </Link>
          <div className="flex items-center gap-8">
            <a href="/#how-it-works" className="text-sm text-[var(--text2)] hover:text-[var(--text)] transition">How it works</a>
            <a href="/#features" className="text-sm text-[var(--text2)] hover:text-[var(--text)] transition">Features</a>
            <a href="#" className="text-sm text-[var(--text2)] hover:text-[var(--text)] transition">GitHub ↗</a>
            <Link to="/quiz" className="text-sm font-medium px-4 py-2 bg-[var(--accent)] text-white rounded hover:bg-[var(--accent2)] transition">
              Start Assessment
            </Link>
          </div>
        </div>
      </nav>

      <main>
        <Outlet />
      </main>

      <Toaster position="bottom-right" />
    </div>
  );
};

export default Layout;
