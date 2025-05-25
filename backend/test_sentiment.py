from sentiment import analyse_sentiment
import json

def print_analysis_results(text, result):
    print("\n" + "="*50)
    print(f"Analyzing text: \"{text}\"")
    print("="*50)
    
    # Print basic results
    print("\n📊 Basic Results:")
    print(f"Dominant Emotion: {result['dominant_emotion']}")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    
    # Print emotion distribution
    print("\n🎭 Emotion Distribution:")
    for emotion, score in result['emotions'].items():
        percentage = score * 100
        bars = "█" * int(percentage/5)  # Create a visual bar
        print(f"{emotion:10} {percentage:5.1f}% {bars}")
    
    # Print detailed metrics
    print("\n📈 Classification Metrics:")
    metrics = result['classification_metrics']
    print(f"Certainty Score: {metrics['certainty_score']*100:.1f}%")
    print(f"Model Used: {metrics['analysis_metadata']['model']}")
    print(f"Text Length: {metrics['analysis_metadata']['text_length']} characters")
    print(f"Emotions Detected: {metrics['analysis_metadata']['emotions_detected']}")

def run_examples():
    # Example 1: Happy text
    happy_text = "I am absolutely thrilled and excited about this amazing project! The results are fantastic!"
    happy_result = analyse_sentiment(happy_text)
    print_analysis_results(happy_text, happy_result)
    
    # Example 2: Sad text
    sad_text = "I feel so disappointed and heartbroken about what happened. Everything went wrong."
    sad_result = analyse_sentiment(sad_text)
    print_analysis_results(sad_text, sad_result)
    
    # Example 3: Mixed emotions
    mixed_text = "While I'm happy about the promotion, I'm also anxious about the new responsibilities."
    mixed_result = analyse_sentiment(mixed_text)
    print_analysis_results(mixed_text, mixed_result)
    
    # Example 4: Neutral text
    neutral_text = "The sky is blue and the temperature is 20 degrees celsius."
    neutral_result = analyse_sentiment(neutral_text)
    print_analysis_results(neutral_text, neutral_result)

if __name__ == "__main__":
    run_examples() 