import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">
          <span role="img" aria-label="sentiment">🎭</span> Sentiment Analysis
        </Link>
      </div>
      <div className="nav-links">
        <Link 
          to="/text-analysis" 
          className={location.pathname === '/text-analysis' ? 'active' : ''}
        >
          <span role="img" aria-label="text">📝</span> Text Analysis
        </Link>
        <Link 
          to="/twitter-analysis"
          className={location.pathname === '/twitter-analysis' ? 'active' : ''}
        >
          <span role="img" aria-label="twitter">🐦</span> Twitter Analysis
        </Link>
      </div>
    </nav>
  );
};

export default Navbar; 