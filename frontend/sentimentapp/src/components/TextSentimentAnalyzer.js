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
import './AnalyzerStyles.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

const TextSentimentAnalyzer = () => {
  const [inputText, setInputText] = useState('');
  const [emotions, setEmotions] = useState({});
  const [loading, setLoading] = useState(false);
  const [dominantEmotion, setDominantEmotion] = useState('');
  const [error, setError] = useState('');

  const analyzeText = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/analyze-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze text');
      }

      const data = await response.json();
      setEmotions(data.emotions);
      setDominantEmotion(data.dominant_emotion);
    } catch (error) {
      console.error('Error analyzing text:', error);
      setError(error.message || 'An error occurred during analysis');
      setEmotions({});
      setDominantEmotion('');
    }
    setLoading(false);
  };

  const chartData = {
    labels: Object.keys(emotions),
    datasets: [
      {
        data: Object.values(emotions),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
        ],
      },
    ],
  };

  return (
    <div className="container">
      <h1>Text Sentiment Analysis</h1>
      <div className="input-section">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter text to analyze..."
          rows={4}
          className="text-input"
        />
        <button
          onClick={analyzeText}
          disabled={loading || !inputText}
          className="analyze-button"
        >
          {loading ? 'Analyzing...' : 'Analyze Sentiment'}
        </button>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      {Object.keys(emotions).length > 0 && (
        <div className="chart-section">
          {dominantEmotion && (
            <div className="dominant-emotion">
              Dominant Emotion: {dominantEmotion.charAt(0).toUpperCase() + dominantEmotion.slice(1)}
            </div>
          )}
          <h2>Emotion Distribution</h2>
          <Pie data={chartData} />
        </div>
      )}
    </div>
  );
};

export default TextSentimentAnalyzer; 