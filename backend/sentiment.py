import re
import nltk
import numpy as np
from collections import defaultdict
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize
from transformers import pipeline

# Initialize the emotion classifier with a better model
emotion_classifier = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    top_k=None
)

def preprocess_text(text):
    """Clean and prepare text for analysis."""
    # Remove extra spaces and newlines
    text = text.strip()
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text

def analyse_sentiment(text):
    """
    Analyze the emotions in the given text using an advanced model.
    Returns a dictionary containing:
    - emotions: Dictionary of emotion scores
    - dominant_emotion: The strongest emotion
    - confidence: Confidence score for the dominant emotion
    - classification_metrics: Detailed metrics about the classification
    """
    try:
        # Preprocess text
        text = preprocess_text(text)
        
        # Get emotion scores
        emotion_scores = emotion_classifier(text)[0]
        
        # Convert to dictionary format
        emotions = {item['label']: float(item['score']) for item in emotion_scores}
        
        # Filter out very low probability emotions (reduces noise)
        threshold = 0.05  # 5% threshold
        emotions = {k: v for k, v in emotions.items() if v >= threshold}
        
        if not emotions:
            # If all emotions were below threshold, keep the top one
            max_emotion = max(emotion_scores, key=lambda x: x['score'])
            emotions = {max_emotion['label']: float(max_emotion['score'])}
        
        # Renormalize the remaining emotions
        total = sum(emotions.values())
        emotions = {k: v/total for k, v in emotions.items()}
        
        # Get dominant emotion and its confidence
        dominant_item = max(emotions.items(), key=lambda x: x[1])
        dominant_emotion = dominant_item[0]
        confidence = dominant_item[1]
        
        # Calculate entropy (uncertainty measure)
        entropy = -sum([score * np.log2(score) if score > 0 else 0 
                       for score in emotions.values()])
        max_entropy = -np.log2(1/len(emotions))  # Maximum possible entropy
        certainty = 1 - (entropy / max_entropy)  # Scale between 0 and 1
        
        # Calculate emotion intensity
        intensity = 1 - emotions.get('neutral', 0)
        
        # Prepare classification metrics
        classification_metrics = {
            'confidence_score': float(confidence),
            'certainty_score': float(certainty),
            'intensity_score': float(intensity),
            'emotion_distribution': emotions,
            'raw_scores': {k: float(v) for k, v in emotions.items()},
            'analysis_metadata': {
                'model': 'roberta-base-go_emotions',
                'emotions_detected': len(emotions),
                'text_length': len(text),
                'significant_emotions': [k for k, v in emotions.items() if v >= 0.1]  # Emotions with >10% probability
            }
        }
        
        return {
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'confidence': confidence,
            'classification_metrics': classification_metrics
        }
        
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return {
            'emotions': {},
            'dominant_emotion': None,
            'confidence': 0.0,
            'classification_metrics': {
                'error': str(e)
            }
        }

def dominant_emotion(emotions):
    """Find the dominant emotion from the emotion scores."""
    if not emotions:
        return None
    return max(emotions.items(), key=lambda x: x[1])[0]

# Example usage and testing
if __name__ == "__main__":
    test_texts = [
        "I am really happy and excited about this project!",
        "This makes me so angry and frustrated!",
        "I'm feeling a bit nervous about the presentation.",
        "What an amazing and wonderful surprise!",
        "The movie was just okay, nothing special.",
        "I'm devastated by the news."
    ]
    
    print("Testing Emotion Analysis with Multiple Examples\n")
    for text in test_texts:
        print("\n" + "="*50)
        print(f"Text: {text}")
        result = analyse_sentiment(text)
        print("\nEmotions Detected:")
        for emotion, score in result['emotions'].items():
            print(f"{emotion:15} : {score*100:5.1f}%")
        print(f"\nDominant Emotion: {result['dominant_emotion']}")
        print(f"Confidence: {result['confidence']*100:.1f}%")
        print(f"Certainty Score: {result['classification_metrics']['certainty_score']*100:.1f}%")
        if 'intensity_score' in result['classification_metrics']:
            print(f"Emotional Intensity: {result['classification_metrics']['intensity_score']*100:.1f}%")