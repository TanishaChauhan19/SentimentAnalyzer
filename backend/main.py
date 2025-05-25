from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sentiment
from twitter_api import fetch_tweets_by_hashtag, get_rate_limit_status

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class TweetRequest(BaseModel):
    hashtag: str
    max_tweets: Optional[int] = 100

class TweetResponse(BaseModel):
    analyzed_tweets: List[Dict]
    cached: bool = False
    summary: str = ""

@app.post("/analyze-text")
async def analyze_text(request: TextRequest):
    try:
        emotions = sentiment.analyze_text(request.text)
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        return {"emotions": emotions, "dominant_emotion": dominant_emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-tweets", response_model=TweetResponse)
async def analyze_tweets(request: TweetRequest):
    try:
        # Fetch tweets (this will use cache if available)
        tweets_result = fetch_tweets_by_hashtag(request.hashtag, request.max_tweets)
        
        if not tweets_result:
            raise HTTPException(
                status_code=404,
                detail=f"No tweets found for hashtag #{request.hashtag}"
            )
        
        # Check if we got cached results
        is_cached = hasattr(tweets_result, 'from_cache') and tweets_result.from_cache
        
        # Get summary if available
        summary = getattr(tweets_result, 'summary', '')
        
        # Analyze each tweet
        analyzed_tweets = []
        for tweet in tweets_result:
            emotions = sentiment.analyze_text(tweet)
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            analyzed_tweets.append({
                "tweet": tweet,
                "emotions": emotions,
                "dominant_emotion": dominant_emotion
            })
        
        return TweetResponse(
            analyzed_tweets=analyzed_tweets,
            cached=is_cached,
            summary=summary
        )
        
    except Exception as e:
        if "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail=str(e)
            )
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 