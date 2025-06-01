import React, { useState } from 'react';
import TextSentimentAnalyzer from './TextSentimentAnalyzer';
import TwitterSentimentAnalyzer from './TwitterSentimentAnalyzer';
import './app1.css';
export default function SelectMode() {
    const [activeTab, setActiveTab] = useState('text'); // 'text' or 'twitter'

    return (
      <div className="App">
        <div className="tab-navigation">
          <button className='btn1'
            onClick={() => setActiveTab('text')}
            style={{
             
            }}
          >
            Text Analysis
          </button>
          <button className='btn1'
            onClick={() => setActiveTab('twitter')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: activeTab === 'twitter' ? '#1DA1F2' : '#fff',
              color: activeTab === 'twitter' ? '#fff' : '#1DA1F2',
              border: '1px solid #1DA1F2',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Twitter Analysis
          </button>
        </div>
        
        {activeTab === 'text' ? <TextSentimentAnalyzer /> : <TwitterSentimentAnalyzer />}
      </div>
    );
  }



