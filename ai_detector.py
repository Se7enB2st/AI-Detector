from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Tuple, Dict, List
import logging
import sys
import argparse
import json
from pathlib import Path
from transformers.pipelines.base import PipelineException
import numpy as np
from textstat import textstat
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIDetector:
    def __init__(self):
        """
        Initialize the AI detector using multiple models and analysis techniques.
        
        Raises:
            RuntimeError: If model initialization fails
        """
        try:
            # Initialize multiple models for ensemble detection
            self.models = {
                'gpt2': pipeline(
                    "text-classification",
                    model="microsoft/DialogRPT-human-vs-rand",
                    device=-1
                ),
                'roberta': pipeline(
                    "text-classification",
                    model="roberta-base-openai-detector",
                    device=-1
                )
            }
            
            # Initialize tokenizer for additional analysis
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            
            logger.info("AI detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI detector: {str(e)}")
            raise RuntimeError(f"Failed to initialize AI detector: {str(e)}")
    
    def _analyze_text_features(self, text: str) -> Dict[str, float]:
        """
        Analyze various text features that might indicate AI generation.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, float]: Dictionary of feature scores
        """
        features = {}
        
        # Calculate perplexity-like score
        tokens = self.tokenizer(text, return_tensors="pt")
        input_ids = tokens["input_ids"]
        attention_mask = tokens["attention_mask"]
        
        # Calculate average token probability
        with torch.no_grad():
            outputs = self.models['gpt2'].model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            avg_prob = probs.mean().item()
        
        features['token_probability'] = avg_prob
        
        # Calculate text statistics
        features['readability'] = textstat.flesch_reading_ease(text)
        features['sentence_length'] = len(re.split(r'[.!?]+', text))
        features['word_length'] = len(text.split())
        features['avg_word_length'] = np.mean([len(word) for word in text.split()])
        
        return features
    
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detect whether the given text is AI-generated or human-written using ensemble methods.
        
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
            
            # Get predictions from multiple models
            predictions = []
            confidences = []
            
            for model_name, model in self.models.items():
                result = model(text)[0]
                label = "AI" if result["label"] == "LABEL_1" else "Human"
                confidence = result["score"]
                predictions.append(label)
                confidences.append(confidence)
            
            # Analyze text features
            features = self._analyze_text_features(text)
            
            # Calculate final score using ensemble method
            final_confidence = np.mean(confidences)
            
            # Adjust confidence based on text features
            if features['token_probability'] > 0.5:
                final_confidence *= 1.2  # Increase confidence if token probability is high
            if features['readability'] > 80:
                final_confidence *= 0.8  # Decrease confidence if text is very readable
            
            # Determine final label
            ai_count = predictions.count("AI")
            human_count = predictions.count("Human")
            
            if ai_count > human_count:
                final_label = "AI"
            else:
                final_label = "Human"
            
            # Ensure confidence is between 0 and 1
            final_confidence = min(max(final_confidence, 0), 1)
            
            logger.info(f"Detection completed: {final_label} (Confidence: {final_confidence:.2f})")
            return final_label, final_confidence
            
        except PipelineException as e:
            logger.error(f"Pipeline error during detection: {str(e)}")
            raise RuntimeError(f"Failed to process text: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during detection: {str(e)}")
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

    def batch_detect(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Process multiple texts in batch.
        
        Args:
            texts (List[str]): List of texts to analyze
            
        Returns:
            List[Dict[str, any]]: List of results with predictions and confidence scores
        """
        results = []
        for i, text in enumerate(texts, 1):
            try:
                label, confidence = self.detect(text)
                results.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "prediction": label,
                    "confidence": confidence,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "error": str(e),
                    "status": "error"
                })
        return results

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

def process_directory(directory: str, detector: AIDetector, output_format: str = "text") -> None:
    """
    Process all text files in a directory.
    
    Args:
        directory (str): Path to the directory
        detector (AIDetector): Initialized AI detector instance
        output_format (str): Output format ('text' or 'json')
    """
    try:
        path = Path(directory)
        if not path.is_dir():
            raise ValueError(f"'{directory}' is not a valid directory")
            
        text_files = list(path.glob("*.txt"))
        if not text_files:
            print(f"No .txt files found in {directory}")
            return
            
        results = []
        for file_path in text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    label, confidence = detector.detect(text)
                    results.append({
                        "file": str(file_path),
                        "prediction": label,
                        "confidence": confidence
                    })
            except Exception as e:
                results.append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        if output_format == "json":
            print(json.dumps(results, indent=2))
        else:
            for result in results:
                if "error" in result:
                    print(f"\nFile: {result['file']}")
                    print(f"Error: {result['error']}")
                else:
                    print(f"\nFile: {result['file']}")
                    print(f"Prediction: {result['prediction']}")
                    print(f"Confidence: {result['confidence']:.2f}")
                    
    except Exception as e:
        print(f"Error processing directory: {str(e)}")
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
  
  # Analyze multiple files in a directory
  python ai_detector.py --dir ./text_files --format json
  
  # Run in interactive mode
  python ai_detector.py --interactive
  
  # Process multiple texts in batch
  python ai_detector.py --batch "text1" "text2" "text3"
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', type=str, help='Text to analyze')
    group.add_argument('--file', type=str, help='Path to text file to analyze')
    group.add_argument('--dir', type=str, help='Directory containing text files to analyze')
    group.add_argument('--batch', nargs='+', help='Multiple texts to analyze')
    group.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    try:
        detector = AIDetector()
        
        if args.text:
            label, confidence = detector.detect(args.text)
            print(f"\nPrediction: {label}")
            print(f"Confidence: {confidence:.2f}")
            
        elif args.file:
            process_file(args.file, detector)
            
        elif args.dir:
            process_directory(args.dir, detector, args.format)
            
        elif args.batch:
            results = detector.batch_detect(args.batch)
            if args.format == "json":
                print(json.dumps(results, indent=2))
            else:
                for result in results:
                    if result["status"] == "error":
                        print(f"\nText: {result['text']}")
                        print(f"Error: {result['error']}")
                    else:
                        print(f"\nText: {result['text']}")
                        print(f"Prediction: {result['prediction']}")
                        print(f"Confidence: {result['confidence']:.2f}")
            
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