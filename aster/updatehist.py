import json
from openai import OpenAI
import os

def convert_to_json(note_text):
    """
    Convert clinical note text to JSON format using OpenAI's GPT-4.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "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"))
    prompt = (f"Convert the following clinical note into a structured JSON format suitable for a medical record. "
              f"Here is the clinical note:\n{note_text}\n"
              "Format the output as a JSON object with appropriate fields based on the output sections, it will be "
              "going in a fhir style format.")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant expected to format medical notes into JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    print("API Response:", response)
    try:
        # Assuming the response is formatted as a stringified JSON
        note_json = json.loads(response.choices[0].message.content.strip())
        return note_json
    except json.JSONDecodeError as e:
        print("Failed to decode JSON from response:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None


def update_patient_history(note_text, file_path='path_to_your_patient_history_file.json'):
    """
    Update the patient history JSON file with new clinical note data.
    """
    note_json = convert_to_json(note_text)
    if note_json is not None:
        with open(file_path, 'r+') as file:
            patient_history = json.load(file)
            patient_history['entry'].append({'resource': note_json})
            file.seek(0)
            json.dump(patient_history, file, indent=4)
    else:
        print("Error: Note JSON conversion failed, no update made to the file.")

# If needed as standalone script
if __name__ == '__main__':
    clinical_note_text = "Placeholder text for clinical note"
    update_patient_history(clinical_note_text)
