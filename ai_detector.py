from transformers import pipeline
from typing import Tuple, Dict

class AIDetector:
    def __init__(self):
        """
        Initialize the AI detector using the roberta-base-openai-detector model.
        """
        self.classifier = pipeline(
            "text-classification",
            model="roberta-base-openai-detector",
            device=-1  # Use CPU by default
        )
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect whether the given text is AI-generated or human-written.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Tuple[str, float]: A tuple containing the prediction label and confidence score
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")
            
        result = self.classifier(text)[0]
        label = "AI" if result["label"] == "LABEL_1" else "Human"
        confidence = result["score"]
        
        return label, confidence

def main():
    # Example usage
    detector = AIDetector()
    
    # Example texts
    ai_text = "The quick brown fox jumps over the lazy dog. This is a common example sentence used for testing."
    human_text = "I went to the store yesterday and bought some groceries. The weather was nice, so I walked home."
    
    # Test AI detection
    print("Testing AI detection...")
    print("\nAI-generated text example:")
    label, confidence = detector.detect(ai_text)
    print(f"Prediction: {label} (Confidence: {confidence:.2f})")
    
    print("\nHuman-written text example:")
    label, confidence = detector.detect(human_text)
    print(f"Prediction: {label} (Confidence: {confidence:.2f})")

if __name__ == "__main__":
    main() 