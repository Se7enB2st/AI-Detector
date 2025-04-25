from transformers import pipeline
from typing import Tuple, Dict
import logging
import sys
from transformers.pipelines.base import PipelineException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIDetector:
    def __init__(self):
        """
        Initialize the AI detector using the roberta-base-openai-detector model.
        
        Raises:
            RuntimeError: If model initialization fails
        """
        try:
            self.classifier = pipeline(
                "text-classification",
                model="roberta-base-openai-detector",
                device=-1  # Use CPU by default
            )
            logger.info("AI detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI detector: {str(e)}")
            raise RuntimeError(f"Failed to initialize AI detector: {str(e)}")
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect whether the given text is AI-generated or human-written.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Tuple[str, float]: A tuple containing the prediction label and confidence score
            
        Raises:
            ValueError: If input text is empty or invalid
            RuntimeError: If detection fails
        """
        try:
            if not isinstance(text, str):
                raise ValueError("Input must be a string")
                
            if not text.strip():
                raise ValueError("Input text cannot be empty")
            
            if len(text) < 10:
                logger.warning("Input text is very short, which may affect detection accuracy")
            
            result = self.classifier(text)[0]
            label = "AI" if result["label"] == "LABEL_1" else "Human"
            confidence = result["score"]
            
            logger.info(f"Detection completed: {label} (Confidence: {confidence:.2f})")
            return label, confidence
            
        except PipelineException as e:
            logger.error(f"Pipeline error during detection: {str(e)}")
            raise RuntimeError(f"Failed to process text: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during detection: {str(e)}")
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

def main():
    try:
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
        
        # Test error handling
        print("\nTesting error handling...")
        try:
            detector.detect("")  # Empty text
        except ValueError as e:
            print(f"Expected error caught: {str(e)}")
            
        try:
            detector.detect(123)  # Invalid input type
        except ValueError as e:
            print(f"Expected error caught: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 