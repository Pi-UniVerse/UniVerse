from django.http import JsonResponse, FileResponse
from gtts import gTTS
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def text_to_speech(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")
        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # Génération du fichier audio
        tts = gTTS(text=text, lang="fr")
        output_path = os.path.join(settings.BASE_DIR, "tts_output.mp3")
        tts.save(output_path)

        return FileResponse(open(output_path, "rb"), content_type="audio/mpeg")
    else:
        return JsonResponse({"error": "POST request required"}, status=405)
