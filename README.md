# Sentiment Analysis Application

A sophisticated sentiment analysis application that uses advanced ML models to analyze emotions in text.

## Setup

1. Clone the repository
```bash
git clone https://github.com/TanishaChauhan19/SentimentAnalyzer.git
cd SentimentAnalyzer
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Environment Variables
Create a `.env` file in the root directory with the following variables:
```
API_KEY=your_api_key_here
BEARER_TOKEN=your_bearer_token
TWITTER_API_SECRET=your_TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN=your_TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET=your_TWITTER_ACCESS_TOKEN_SECRET
MODEL_PATH=your_model_path_here
PORT=8000
HOST=localhost
```

## Running the Application

1. Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend:
```bash
cd frontend/sentimentapp
npm install
npm start
```

## Features

- Advanced emotion detection using SamLowe/roberta-base-go_emotions model
- Comprehensive emotion classification with multiple categories
- High-accuracy sentiment predictions
- Confidence scoring and certainty metrics
- Emotion intensity measurement
- Detailed classification metrics including:
  - Confidence scores
  - Certainty scores
  - Emotion distribution
  - Significant emotions detection
- User-friendly interface

## Model Details
The application uses the `SamLowe/roberta-base-go_emotions` model from Hugging Face, which:
- Provides balanced emotion detection
- Supports multiple emotion categories
- Filters out low-probability emotions
- Includes confidence and certainty metrics
- Automatically downloads when first run

## Security Notes

- Never commit your `.env` file
- Keep your API keys and credentials secure
- Use environment variables for sensitive information