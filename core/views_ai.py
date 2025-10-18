from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .ai_utils import (
    translate_text, 
    detect_language,
    analyze_sentiment,
    detect_toxic_content,
    generate_hashtags
)
import json
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def ai_suggestions(request):
    """Get AI-powered content suggestions"""
    try:
        # Parse JSON body
        body = request.body.decode('utf-8')
        logger.info(f"Received body: {body}")
        
        data = json.loads(body)
        text = data.get('text', '').strip()
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'No text provided'
            }, status=400)
        
        # Limit text length
        text = text[:500]
        
        logger.info(f"Analyzing text: {text[:50]}...")
        
        # Generate hashtags
        hashtags = generate_hashtags(text)
        logger.info(f"Generated hashtags: {hashtags}")
        
        # Analyze sentiment
        sentiment = None
        try:
            sentiment = analyze_sentiment(text)
            logger.info(f"Sentiment: {sentiment}")
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
        
        # Check toxicity
        toxicity = None
        try:
            toxicity = detect_toxic_content(text)
            logger.info(f"Toxicity: {toxicity}")
        except Exception as e:
            logger.error(f"Toxicity detection error: {e}")
        
        return JsonResponse({
            'success': True,
            'hashtags': hashtags if hashtags else [],
            'sentiment': sentiment,
            'toxicity': toxicity if toxicity else {'is_toxic': False, 'score': 0}
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in ai_suggestions: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def translate_post(request):
    """Translate post content in real-time"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text', '').strip()
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'No text provided'
            }, status=400)
        
        # Detect source language
        source_lang = detect_language(text)
        logger.info(f"Detected language: {source_lang}")
        
        # Translate
        translated = translate_text(text, target_lang)
        logger.info(f"Translated to {target_lang}")
        
        return JsonResponse({
            'success': True,
            'translated_text': translated,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def analyze_image(request):
    """Analyze uploaded image and return AI-generated caption"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image provided'
            }, status=400)
        
        image_file = request.FILES['image']
        
        # Save temporarily
        temp_path = None
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            logger.info(f"Analyzing image: {temp_path}")
            
            # Generate caption
            from .ai_utils import generate_image_description
            caption = generate_image_description(temp_path)
            
            if caption:
                return JsonResponse({
                    'success': True,
                    'caption': caption
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Could not generate caption'
                }, status=500)
                
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Image analysis error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
