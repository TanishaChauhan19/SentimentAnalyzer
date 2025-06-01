import React, { useState } from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
} from 'chart.js';
import Navbar from './Navbar';
import Modal from './Modal';
import './AnalyzerStyles.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

const TwitterSentimentAnalyzer = () => {
  const [hashtag, setHashtag] = useState('');
  const [emotions, setEmotions] = useState({});
  const [loading, setLoading] = useState(false);
  const [tweets, setTweets] = useState([]);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [dominantEmotion, setDominantEmotion] = useState('');
  const [analyzedTweets, setAnalyzedTweets] = useState([]);
  const [isUsingCache, setIsUsingCache] = useState(false);
  const [summary, setSummary] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const analyzeHashtag = async () => {
    setLoading(true);
    setError('');
    setStatus('Analyzing tweets...');
    setIsUsingCache(false);
    setSummary('');
    
    try {
      const requestBody = {
        hashtag: hashtag.replace('#', '').trim(),
        max_tweets: 10
      };
      console.log('Request body:', requestBody);
      const response = await fetch('http://localhost:8000/analyze-tweets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('Raw response:', response);
      const data = await response.json();
      console.log('Response JSON:', data);
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze tweets');
      }

      setIsUsingCache(data.cached);
      setSummary(data.summary);
      
      if (data.analyzed_tweets.length === 0) {
        throw new Error('No tweets found for this hashtag');
      }

      // Calculate aggregate emotions from all tweets
      const aggregateEmotions = {};
      let emotionCounts = {};
      
      data.analyzed_tweets.forEach(tweet => {
        Object.entries(tweet.emotions).forEach(([emotion, score]) => {
          aggregateEmotions[emotion] = (aggregateEmotions[emotion] || 0) + score;
        });
        
        emotionCounts[tweet.dominant_emotion] = (emotionCounts[tweet.dominant_emotion] || 0) + 1;
      });

      const tweetCount = data.analyzed_tweets.length;
      Object.keys(aggregateEmotions).forEach(emotion => {
        aggregateEmotions[emotion] = aggregateEmotions[emotion] / tweetCount;
      });

      const overallDominantEmotion = Object.entries(emotionCounts)
        .reduce((a, b) => (a[1] > b[1] ? a : b))[0];

      setEmotions(aggregateEmotions);
      setDominantEmotion(overallDominantEmotion);
      setTweets(data.analyzed_tweets.map(t => t.tweet));
      setAnalyzedTweets(data.analyzed_tweets);
      setStatus(isUsingCache ? 'Showing cached results' : 'Analysis complete!');
      setIsModalOpen(true); // Open modal when analysis is complete
    } catch (error) {
      console.error('Error:', error);
      let errorMsg = 'An error occurred during analysis';
      if (typeof error === 'string') {
        errorMsg = error;
      } else if (error instanceof Error) {
        errorMsg = error.message;
      } else if (error && typeof error === 'object') {
        if (error.detail) {
          errorMsg = typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail);
        } else if (error.message) {
          errorMsg = error.message;
        } else {
          errorMsg = JSON.stringify(error);
        }
      }
      setError(errorMsg);
      setEmotions({});
      setDominantEmotion('');
      setTweets([]);
      setAnalyzedTweets([]);
      setSummary('');
    }
    setLoading(false);
  };

  const chartData = {
    labels: Object.keys(emotions),
    datasets: [
      {
        data: Object.values(emotions),
        backgroundColor: [
          '#FF6384', // sadness
          '#36A2EB', // anger
          '#FFCE56', // joy
          '#4BC0C0', // disgust
          '#9966FF', // surprise
          '#FF9F40', // fear
          '#B0B0B0', // neutral
        ],
      },
    ],
  };

  const chartOptions = {
    plugins: {
      legend: {
        position: 'right',
        labels: {
          font: {
            size: 14,
            family: "'Segoe UI', 'Roboto', sans-serif"
          },
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.raw || 0;
            return `${label}: ${(value * 100).toFixed(1)}%`;
          }
        }
      }
    },
    layout: {
      padding: 20
    },
    maintainAspectRatio: false
  };

  return (
    <>
      <Navbar />
      <div className="analyzer-container">
        <h1 className="analyzer-title">Twitter Hashtag Analysis</h1>
        <div className="input-section">
          <div className="hashtag-input">
            <input
              type="text"
              value={hashtag}
              onChange={(e) => setHashtag(e.target.value)}
              placeholder="Enter hashtag (e.g., AI or #AI)"
            />
          </div>
          <button
            onClick={analyzeHashtag}
            disabled={loading || !hashtag}
            className={`analyze-button ${loading ? 'loading' : ''}`}
          >
            {loading ? '' : 'Analyze Twitter Sentiment'}
          </button>

          {summary && (
            <div className="summary-container">
              <h3 className="summary-title">Tweet Summary</h3>
              <div className="summary-content">{summary}</div>
            </div>
          )}

          {isUsingCache && (
            <div className="cache-notice">
              Note: Showing cached results from previous analysis
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {tweets.length > 0 && (
            <div className="analysis-status">
              <p>Analyzed {tweets.length} tweets with #{hashtag}</p>
            </div>
          )}
        </div>

        <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
          <div className="results-container">
            <div className="chart-section">
              {dominantEmotion && (
                <div className="dominant-emotion">
                  Overall Dominant Emotion: {dominantEmotion.charAt(0).toUpperCase() + dominantEmotion.slice(1)}
                </div>
              )}
              <h2>Average Sentiment Distribution</h2>
              <div className="chart-container">
                <Pie data={chartData} options={chartOptions} />
              </div>
            </div>

            {analyzedTweets.length > 0 && (
              <div className="tweets-container">
                <h3>Individual Tweet Analysis</h3>
                <div className="tweets-list">
                  {analyzedTweets.map((tweet, index) => (
                    <div key={index} className="tweet-item">
                      <p className="tweet-text">{tweet.tweet}</p>
                      <small className="tweet-emotion">
                        Dominant Emotion: {tweet.dominant_emotion}
                      </small>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      </div>
    </>
  );
};

export default TwitterSentimentAnalyzer; 