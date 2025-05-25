from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from twitter_api import fetch_tweets_by_hashtag
from sentiment import analyse_sentiment, dominant_emotion
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any

# Create FastAPI app with metadata for documentation
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for analyzing sentiments in text and Twitter hashtags",
    version="1.0.0",
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for API health check
@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to Sentiment Analysis API", "status": "active"}

# Request models
class TextRequest(BaseModel):
    text: str

class HashtagRequest(BaseModel):
    hashtag: str
    max_tweets: int = 100

class ClassificationMetrics(BaseModel):
    confidence_score: float
    certainty_score: float
    emotion_distribution: Dict[str, float]
    raw_scores: Dict[str, float]
    analysis_metadata: Dict[str, Any]

class EmotionResponse(BaseModel):
    emotions: Dict[str, float]
    dominant_emotion: str
    confidence: float
    classification_metrics: ClassificationMetrics

class TweetAnalysis(BaseModel):
    tweet: str
    emotions: Dict[str, float]
    dominant_emotion: str
    confidence: float
    classification_metrics: ClassificationMetrics

class TwitterResponse(BaseModel):
    hashtag: str
    total_tweets: int
    analyzed_tweets: List[TweetAnalysis]
    cached: bool = False
    summary: str = ""

@app.post("/analyze-text", response_model=EmotionResponse, tags=["Sentiment Analysis"])
async def analyze_text(request: TextRequest):
    """
    Analyze the emotions in a given text with detailed classification metrics.
    
    Parameters:
    - text: The text to analyze
    
    Returns:
    - emotions: Dictionary of emotions and their scores
    - dominant_emotion: The strongest emotion detected
    - confidence: Confidence score for the dominant emotion
    - classification_metrics: Detailed metrics about the classification
    """
    try:
        # Analyze emotions
        result = analyse_sentiment(request.text)
        if not result or not result['emotions']:
            raise HTTPException(status_code=500, detail="Failed to analyze emotions")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-tweets", response_model=TwitterResponse, tags=["Twitter Analysis"])
async def analyze_tweets(request: HashtagRequest):
    """
    Analyze emotions in tweets containing a specific hashtag with detailed metrics.
    
    Parameters:
    - hashtag: The hashtag to search for (with or without #)
    - max_tweets: Maximum number of tweets to analyze (default: 100)
    
    Returns:
    - hashtag: The analyzed hashtag
    - total_tweets: Number of tweets analyzed
    - analyzed_tweets: List of analyzed tweets with detailed emotion metrics
    - cached: Whether the results came from cache
    - summary: A summary of the analysis
    """
    try:
        # Fetch tweets
        tweets_result = fetch_tweets_by_hashtag(request.hashtag, request.max_tweets)
        if not tweets_result:
            return TwitterResponse(
                hashtag=request.hashtag,
                total_tweets=0,
                analyzed_tweets=[],
                cached=False,
                summary=""
            )

        # Check if we got cached results
        is_cached = hasattr(tweets_result, 'from_cache') and tweets_result.from_cache
        
        # Get summary if available
        summary = getattr(tweets_result, 'summary', '')
        
        # Analyze each tweet
        analyzed = []
        for tweet in tweets_result:
            result = analyse_sentiment(tweet)
            analyzed.append(TweetAnalysis(
                tweet=tweet,
                emotions=result['emotions'],
                dominant_emotion=result['dominant_emotion'],
                confidence=result['confidence'],
                classification_metrics=result['classification_metrics']
            ))

        return TwitterResponse(
            hashtag=request.hashtag,
            total_tweets=len(analyzed),
            analyzed_tweets=analyzed,
            cached=is_cached,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
