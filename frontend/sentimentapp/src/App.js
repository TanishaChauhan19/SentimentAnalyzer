import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TextSentimentAnalyzer from './components/TextSentimentAnalyzer';
import TwitterSentimentAnalyzer from './components/TwitterSentimentAnalyzer';
import FrontPage from './components/FrontPage';
import './styles/global.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<FrontPage />} />
          <Route path="/text-analysis" element={<TextSentimentAnalyzer />} />
          <Route path="/twitter-analysis" element={<TwitterSentimentAnalyzer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;