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
import Navbar from './Navbar';
import Modal from './Modal';
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

const TextSentimentAnalyzer = () => {
  const [inputText, setInputText] = useState('');
  const [emotions, setEmotions] = useState({});
  const [loading, setLoading] = useState(false);
  const [dominantEmotion, setDominantEmotion] = useState('');
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

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
      setIsModalOpen(true);
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
      <h1 className="analyzer-title">Text Sentiment Analysis</h1>
      <div className="input-section">
        <div className="hashtag-input">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text to analyze..."
            rows={4}
            className="text-input"
          />
        </div>
        <button
          onClick={analyzeText}
          disabled={loading || !inputText}
          className={`analyze-button${loading ? ' loading' : ''}`}
        >
          {loading ? '' : 'Analyze Sentiment'}
        </button>
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <div className="results-container">
          <div className="chart-section" style={{ boxShadow: 'none', background: 'rgba(255,255,255,0.95)', borderRadius: '16px', margin: '0 auto', maxWidth: 600 }}>
            {dominantEmotion && (
              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
                <div style={{ background: '#2b8ff9', color: 'white', borderRadius: '16px', padding: '1.2rem 2rem', fontWeight: 700, fontSize: '1.3rem', textAlign: 'center', boxShadow: '0 2px 8px rgba(43,143,249,0.08)' }}>
                  Dominant Emotion: {dominantEmotion.charAt(0).toUpperCase() + dominantEmotion.slice(1)}
                </div>
              </div>
            )}
            <h2 style={{ textAlign: 'center', fontWeight: 700, fontSize: '2rem', marginBottom: '2rem', color: '#222' }}>Emotion Distribution</h2>
            <div className="chart-container" style={{ margin: '0 auto', height: 400, width: '100%' }}>
              <Pie data={chartData} options={chartOptions} />
            </div>
          </div>
        </div>
      </Modal>
    </div>
    </>
  );
};

export default TextSentimentAnalyzer; 