from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import base64
import json
import os
import tempfile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import document

import base64
import tempfile
import whisper
import os
import json

model = whisper.load_model("base")

def home(request):
    # if request.method == 'POST':
    #     print("this workssssssss")
    #     audio_base64 = request.FILES['audio']
    #     audio_file = base64_to_wav(audio_base64)
    #     result = model.transcribe(audio_file)
    #     return JsonResponse({'transcription': result})
    return render(request, 'home.html')

@csrf_exempt
def recording_info(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        audio_base64 = data.get('audio')

        if not audio_base64:
            return HttpResponse("Audio data not found", status=400)

        audio_file_path = base64_to_wav(audio_base64)
        result = model.transcribe(audio_file_path)
        os.remove(audio_file_path)  # Clean up the temporary file

        clinical_notes, _ = document.generate_clinical_notes(result['text'])
        split_index = clinical_notes.find("Assessment:")
        clinical_notes_before_assessment = clinical_notes[:split_index].strip().replace("\n", "<br>")
        assessment_and_plan = clinical_notes[split_index:].strip().replace("\n", "<br>")

        context = {
            'audio_base64': "data:audio/wav;base64," + audio_base64,
            'transcription': result['text'],
            'clinical_notes_before_assessment': clinical_notes_before_assessment,
            'assessment_and_plan': assessment_and_plan,
        }

        return render(request, 'info.html', context)


def base64_to_wav(audio_base64):
    audio_binary = base64.b64decode(audio_base64)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(audio_binary)
        return temp_file.name
