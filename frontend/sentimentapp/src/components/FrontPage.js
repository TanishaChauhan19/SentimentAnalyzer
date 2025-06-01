import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import './FrontPage.css';

const FrontPage = () => {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <div className="front-page">
        <div className="hero-section">
          <h1> Sentiment Analysis Platform </h1>
          <p className="subtitle">
             Analyze emotions and sentiments in text and social media.
          </p>
          
          <div className="analysis-options">
            <div className="option-card" onClick={() => navigate('/text-analysis')}>
              <div className="option-icon">
                <span role="img" aria-label="text analysis">📊</span>
              </div>
              <h2>Text Analysis</h2>
              <p>Discover emotions in any text </p>
              <ul>
                <li>⚡ Real-time emotion detection</li>
                <li>📈 Detailed sentiment breakdown</li>
                <li>🎯 Precise analysis results</li>
                <li>💫 User-friendly interface</li>
              </ul>
              <button className="select-button">
                Start Text Analysis 
              </button>
            </div>

            <div className="option-card" onClick={() => navigate('/twitter-analysis')}>
              <div className="option-icon">
                <span role="img" aria-label="twitter analysis">🐦</span>
              </div>
              <h2>Twitter Analysis</h2>
              <p>Analyze tweet sentimentt in real time.</p>
              <ul>
                <li>🔍 Advanced hashtag analysis</li>
                <li>📊 Trend detection & insights</li>
                <li>📈 Comprehensive reports</li>
                <li>🔄 Real-time updates</li>
              </ul>
              <button className="select-button">
                Start Twitter Analysis 
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default FrontPage;