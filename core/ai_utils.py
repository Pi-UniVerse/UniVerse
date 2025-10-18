"""
AI utilities using free Hugging Face models
No API keys required!
"""
from transformers import pipeline
from PIL import Image
import torch
from langdetect import detect
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

# Initialize models (lazy loading)
_image_caption_model = None
_sentiment_model = None
_text_classifier_model = None
_translator = None


def get_image_caption_model():
    """Load image captioning model (runs locally)"""
    global _image_caption_model
    if _image_caption_model is None:
        try:
            _image_caption_model = pipeline(
                "image-to-text",
                model="Salesforce/blip-image-captioning-base",
                device=-1  # CPU
            )
            logger.info("✅ Image captioning model loaded")
        except Exception as e:
            logger.error(f"❌ Error loading image caption model: {e}")
            _image_caption_model = None
    return _image_caption_model


def get_sentiment_model():
    """Load sentiment analysis model"""
    global _sentiment_model
    if _sentiment_model is None:
        try:
            _sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1
            )
            logger.info("✅ Sentiment model loaded")
        except Exception as e:
            logger.error(f"❌ Error loading sentiment model: {e}")
            _sentiment_model = None
    return _sentiment_model


def get_text_classifier():
    """Load hate speech/toxicity detector"""
    global _text_classifier_model
    if _text_classifier_model is None:
        try:
            _text_classifier_model = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=-1
            )
            logger.info("✅ Toxicity detector loaded")
        except Exception as e:
            logger.error(f"❌ Error loading text classifier: {e}")
            _text_classifier_model = None
    return _text_classifier_model


def get_translator():
    """Get translator instance"""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


# ========== AI FEATURES ==========

def generate_image_description(image_path):
    """
    Generate automatic description for uploaded images
    Perfect for: Accessibility, SEO, auto-captions
    """
    try:
        model = get_image_caption_model()
        if model is None:
            return None
        
        image = Image.open(image_path).convert('RGB')
        result = model(image)
        
        if result and len(result) > 0:
            caption = result[0]['generated_text']
            logger.info(f"✅ Generated caption: {caption}")
            return caption
        
        return None
    except Exception as e:
        logger.error(f"❌ Error generating image description: {e}")
        return None


def analyze_sentiment(text):
    """
    Analyze sentiment of text (positive/negative)
    Perfect for: Content filtering, mood tracking
    """
    try:
        model = get_sentiment_model()
        if model is None:
            return None
        
        result = model(text[:512])  # Limit to 512 chars
        
        if result and len(result) > 0:
            sentiment = result[0]
            return {
                'label': sentiment['label'],  # POSITIVE or NEGATIVE
                'score': sentiment['score']    # Confidence 0-1
            }
        
        return None
    except Exception as e:
        logger.error(f"❌ Error analyzing sentiment: {e}")
        return None


def detect_toxic_content(text):
    """
    Detect hate speech, toxicity, and inappropriate content
    Perfect for: Content moderation
    """
    try:
        model = get_text_classifier()
        if model is None:
            return {'is_toxic': False, 'score': 0}
        
        result = model(text[:512])
        
        if result and len(result) > 0:
            prediction = result[0]
            is_toxic = prediction['label'] == 'toxic'
            score = prediction['score']
            
            return {
                'is_toxic': is_toxic,
                'score': score,
                'label': prediction['label']
            }
        
        return {'is_toxic': False, 'score': 0}
    except Exception as e:
        logger.error(f"❌ Error detecting toxic content: {e}")
        return {'is_toxic': False, 'score': 0}


def detect_language(text):
    """
    Detect language of text
    Perfect for: Auto-translation
    """
    try:
        lang = detect(text)
        return lang
    except Exception as e:
        logger.error(f"❌ Error detecting language: {e}")
        return 'en'


def translate_text(text, target_lang='en'):
    """
    Translate text to target language
    Perfect for: Real-time translation
    """
    try:
        translator = get_translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        logger.error(f"❌ Error translating text: {e}")
        return text


def generate_hashtags(text):
    """
    Generate relevant hashtags from text
    Simple keyword extraction
    """
    try:
        # Simple implementation - extract keywords
        words = text.lower().split()
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 4 and w not in stop_words]
        
        # Take top 3-5 unique keywords
        unique_keywords = list(set(keywords))[:5]
        hashtags = ['#' + word for word in unique_keywords]
        
        return hashtags
    except Exception as e:
        logger.error(f"❌ Error generating hashtags: {e}")
        return []


def summarize_text(text, max_length=100):
    """
    Simple text summarization
    Returns first sentences up to max_length
    """
    try:
        sentences = text.split('.')
        summary = ''
        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence + '.'
            else:
                break
        
        return summary.strip()
    except Exception as e:
        logger.error(f"❌ Error summarizing text: {e}")
        return text[:max_length]