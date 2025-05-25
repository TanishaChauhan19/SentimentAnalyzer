import tweepy
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

# Load environment variables
load_dotenv()

# Twitter API credentials
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Initialize Twitter client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=False  # We'll handle rate limits ourselves
)

# Cache for storing recent searches
tweet_cache: Dict[str, Dict] = {}
CACHE_DURATION = timedelta(minutes=15)  # Cache results for 15 minutes

def clean_tweet(tweet: str) -> str:
    """Clean tweet text by removing URLs, mentions, and special characters"""
    # Remove URLs
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    # Remove mentions
    tweet = re.sub(r'@\w+', '', tweet)
    # Remove hashtags
    tweet = re.sub(r'#\w+', '', tweet)
    # Remove extra whitespace
    tweet = ' '.join(tweet.split())
    return tweet.strip()

def is_spam(tweet: str) -> bool:
    """Check if a tweet might be spam"""
    # Convert to lowercase for checking
    text = tweet.lower()
    
    # Spam indicators
    spam_indicators = [
        # Excessive symbols
        len(re.findall(r'[!?]{2,}', tweet)) > 2,
        # Too many numbers (might be a bot)
        len(re.findall(r'\d+', tweet)) > 5,
        # Repetitive characters
        any(char * 3 in text for char in 'abcdefghijklmnopqrstuvwxyz'),
        # Common spam phrases
        any(phrase in text for phrase in ['click here', 'buy now', 'earn money', 'win prize']),
        # Too many capital letters (shouting)
        sum(1 for c in tweet if c.isupper()) / len(tweet) > 0.5 if tweet else False,
        # Very short content
        len(clean_tweet(tweet).split()) < 3
    ]
    
    return any(spam_indicators)

def summarize_tweets(tweets: List[str]) -> str:
    """Generate a brief summary of the tweets"""
    if not tweets:
        return ""
    
    # Get word frequency
    words = ' '.join([clean_tweet(tweet.lower()) for tweet in tweets]).split()
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Only count words longer than 3 characters
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top mentioned words
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Create summary
    summary = f"Analysis of {len(tweets)} tweets:\n"
    summary += f"• Most discussed topics: {', '.join(word for word, _ in top_words)}\n"
    summary += f"• Average tweet length: {sum(len(tweet.split()) for tweet in tweets) // len(tweets)} words\n"
    summary += f"• Time period: Last {min(24, len(tweets))} hours"
    
    return summary

class CachedTweets(List[str]):
    def __init__(self, tweets, summary=""):
        super().__init__(tweets)
        self.from_cache = True
        self.summary = summary

def get_cached_tweets(hashtag: str) -> Optional[CachedTweets]:
    """Get tweets from cache if they exist and are not expired"""
    if hashtag in tweet_cache:
        cache_entry = tweet_cache[hashtag]
        if datetime.now() - cache_entry['timestamp'] < CACHE_DURATION:
            return CachedTweets(cache_entry['tweets'], cache_entry['summary'])
    return None

def cache_tweets(hashtag: str, tweets: List[str], summary: str):
    """Store tweets in cache with timestamp"""
    tweet_cache[hashtag] = {
        'tweets': tweets,
        'timestamp': datetime.now(),
        'summary': summary
    }

def fetch_tweets_by_hashtag(hashtag: str, max_tweets: int = 20) -> List[str]:
    """
    Fetch tweets containing the specified hashtag with rate limit handling and caching.
    
    Args:
        hashtag (str): Hashtag to search for (with or without #)
        max_tweets (int): Maximum number of tweets to fetch
    
    Returns:
        list: List of tweet texts
    
    Raises:
        Exception: If there's an error fetching tweets
    """
    try:
        # Check cache first
        cached_result = get_cached_tweets(hashtag)
        if cached_result:
            return cached_result

        # Remove # if present and format the query
        hashtag = hashtag.strip().replace('#', '')
        query = f"#{hashtag} -is:retweet lang:en"

        try:
            # Try to fetch tweets
            response = client.search_recent_tweets(
                query=query,
                max_results=min(max_tweets * 2, 100),  # Fetch more to account for filtering
                tweet_fields=['text', 'created_at']
            )
            
            if not response.data:
                return []

            # Filter and clean tweets
            tweets_list = []
            for tweet in response.data:
                tweet_text = tweet.text
                if not is_spam(tweet_text):
                    cleaned_text = clean_tweet(tweet_text)
                    if cleaned_text:  # Only add if there's content after cleaning
                        tweets_list.append(cleaned_text)
                
                if len(tweets_list) >= max_tweets:
                    break

            # Generate summary
            summary = summarize_tweets(tweets_list)
            
            # Cache the results
            cache_tweets(hashtag, tweets_list, summary)
            
            # Create result object with summary
            result = CachedTweets(tweets_list, summary)
            result.from_cache = False
            return result

        except tweepy.TooManyRequests:
            # Check if we have cached results before failing
            cached_result = get_cached_tweets(hashtag)
            if cached_result:
                return cached_result
            raise Exception("Twitter API rate limit reached. Please try again in 15 minutes.")
            
        except tweepy.HTTPException as e:
            # Check if we have cached results before failing
            cached_result = get_cached_tweets(hashtag)
            if cached_result:
                return cached_result
            raise Exception(f"Twitter API error: {str(e)}")

    except Exception as e:
        raise Exception(f"Error fetching tweets: {str(e)}")

def get_rate_limit_status() -> Dict:
    """Get current rate limit status"""
    try:
        # Try a test search to check rate limits
        test_response = client.search_recent_tweets(
            "test",
            max_results=10
        )
        return {"remaining": 1, "reset_time": None}  # If we can make a request, we have remaining calls
    except tweepy.TooManyRequests:
        return {"remaining": 0, "reset_time": None}
    except Exception:
        return {"remaining": "unknown", "reset_time": None}

# Example usage
if __name__ == "__main__":
    try:
        hashtag = "AI"
        print(f"Fetching tweets for #{hashtag}...")
        
        # Check rate limits first
        limits = get_rate_limit_status()
        print(f"Rate limit status: {limits}")
        
        tweets = fetch_tweets_by_hashtag(hashtag, 10)
        print(f"\nFound {len(tweets)} tweets:")
        if hasattr(tweets, 'summary'):
            print("\nSummary:")
            print(tweets.summary)
        print("\nTweets:")
        for i, tweet in enumerate(tweets, 1):
            print(f"\n{i}. {tweet}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
