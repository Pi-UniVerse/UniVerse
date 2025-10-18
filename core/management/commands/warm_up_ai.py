from django.core.management.base import BaseCommand
from core.ai_utils import (
    get_image_caption_model,
    get_sentiment_model,
    get_text_classifier
)

class Command(BaseCommand):
    help = 'Warm up AI models (download and cache them)'

    def handle(self, *args, **options):
        self.stdout.write('🤖 Warming up AI models...')
        
        self.stdout.write('📥 Loading image captioning model...')
        get_image_caption_model()
        
        self.stdout.write('📥 Loading sentiment analysis model...')
        get_sentiment_model()
        
        self.stdout.write('📥 Loading toxicity detector...')
        get_text_classifier()
        
        self.stdout.write(self.style.SUCCESS('✅ All AI models ready!'))