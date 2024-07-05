import os
from openai import OpenAI
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
from pynput.keyboard import Listener, Key
import sys
from . import updatehist   # Import the update function
# use this
# Assuming client initialization and Whisper model loading are done globally
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-RnhDyXl2OBJ9i88RnszwT3BlbkFJ3SF9NM4Jej8otcT4N1Fr"))
model = whisper.load_model("base")

def generate_clinical_notes(conversation):
    prompt = ("Imagine you are a scribe helping a physician with clinical documentation. Please convert the following "
              "brief transcription of a medical consultation into a structured clinic note and absolutely do not add any extra information that is not mentioned. The note should follow "
              "the typical format used in medical documentation, including sections for History, Vitals, Examination, "
              "Assessment, and Plan. The style and tone should closely match previous clinic notes written by the "
              "doctor."
              "Output Format as below. Omit any sections that are not mentioned during the visit."
              "Date"
              "History: Patient's history, reason for the visit, symptoms "
              "and a ny relevant personal or family medical history."
              "Past Medical History"
              "Past Surgical history:"
              "Current Medications"
              "Allergies"
              "Examination: Physical findings and observations made during the consultation. Be specific in medical terminology"
              "labs/imaging findings:"
              "Assessment: Number each individual problem or diagnosis issue as it's own paragraph.   "
              "Then list the plan below it."
              "Plan: Recommended treatment plan, follow-up steps, and any patient instructions."
              "Additional Considerations YOU WILL RECIEVE LANGUAGES OTHER THAN ENGLISH IF YOU DO TRANSLATE FIRST THEN SEE GRAMMAR ERRORS THEN DO THE ABOVE\n") + conversation
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that does not add or infer any details not explicitly mentioned."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,  # Increase if needed based on the average length of notes
        temperature=0.3
    )
    generated_note = response.choices[0].message.content.strip()
    return generated_note, False

def on_press(key):
    # Function to check if the space key is pressed
    if key == Key.space:
        return False  # Stop the listener

def record_audio():
    frames = []
    def callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    print("Press Space to start recording...")
    with Listener(on_press=on_press) as listener:
        listener.join()  # Wait for the first space key press

    print("Recording... Press Space to stop.")
    with sd.InputStream(callback=lambda indata, frame_count, time_info, status: frames.append(indata.copy()),
                        samplerate=16000, channels=1) as stream:
        with Listener(on_press=on_press) as listener:
            listener.join()  # Wait for the second space key press

    print("Recording stopped.")
    audio = np.concatenate(frames, axis=0)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sf.write(temp_file.name, audio, 16000)
    return temp_file.name

def recognize_speech_from_mic():
    audio_file = record_audio()
    result = model.transcribe(audio_file)
    os.remove(audio_file)
    print("Recognized text:", result['text'])
    return result['text']


def edit_output(output):
    edited_output = input("Edit the output as needed:\n")
    if edited_output.strip():
        return edited_output.strip(), True
    else:
        return output, False


if __name__ == "__main__":
    transcript = recognize_speech_from_mic()
    print("Transcription:\n", transcript)
    clinical_notes, edited = generate_clinical_notes(transcript)
    print("Generated Clinical Note:\n", clinical_notes)

    if edited:
        clinical_notes, _ = edit_output(clinical_notes)
        print("Doctors Clinical Note:\n", clinical_notes)
    else:
        print("Press Enter to edit the generated clinical note.")
        input()  # Wait for user to press Enter
        clinical_notes, _ = edit_output(clinical_notes)
        print("Edited Clinical Note:\n", clinical_notes)
    if input("Press 'U' to update the JSON file with the generated clinical note: ").upper() == 'U':
        update_patient_history(clinical_notes)
        print("Clinical note updated in the JSON file.")

# for mongodb trouble shooting: tracert "url"
