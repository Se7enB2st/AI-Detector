from transformers import pipeline
from typing import Tuple, Dict
import logging
import sys
import argparse
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

def process_file(file_path: str, detector: AIDetector) -> None:
    """
    Process a text file and detect AI content.
    
    Args:
        file_path (str): Path to the text file
        detector (AIDetector): Initialized AI detector instance
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            label, confidence = detector.detect(text)
            print(f"\nFile: {file_path}")
            print(f"Prediction: {label}")
            print(f"Confidence: {confidence:.2f}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="AI Text Detector - Detect whether text is AI-generated or human-written",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze text directly
  python ai_detector.py --text "Your text here"
  
  # Analyze text from a file
  python ai_detector.py --file input.txt
  
  # Run in interactive mode
  python ai_detector.py --interactive
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', type=str, help='Text to analyze')
    group.add_argument('--file', type=str, help='Path to text file to analyze')
    group.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    try:
        detector = AIDetector()
        
        if args.text:
            label, confidence = detector.detect(args.text)
            print(f"\nPrediction: {label}")
            print(f"Confidence: {confidence:.2f}")
            
        elif args.file:
            process_file(args.file, detector)
            
        elif args.interactive:
            print("\nAI Text Detector - Interactive Mode")
            print("Type 'exit' to quit")
            print("-" * 50)
            
            while True:
                text = input("\nEnter text to analyze: ").strip()
                if text.lower() == 'exit':
                    break
                    
                if not text:
                    print("Please enter some text")
                    continue
                    
                try:
                    label, confidence = detector.detect(text)
                    print(f"\nPrediction: {label}")
                    print(f"Confidence: {confidence:.2f}")
                except Exception as e:
                    print(f"Error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 