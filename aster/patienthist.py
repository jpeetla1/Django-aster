import json
from openai import OpenAI
import os

def load_json_from_file(file_path):
    """
    Load JSON data from a file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def query_openai(json_data):
    """
    Send JSON data to OpenAI's GPT-4 and get a human-readable interpretation.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-jVepFOdZ6uD1rWO9o19ET3BlbkFJUGZVvGxVCqwr2HGqYIJT"))
    prompt = f"Here is a JSON data representing medical records. Please provide a detailed, human-readable interpretation of the information:\n\n{json.dumps(json_data, indent=2)}"
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled in interpreting and summarizing medical data."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,  # Increased token limit for potentially large input
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Load JSON data from file
    file_path = 'records.JSON'  # Ensure this file path is correct and accessible
    json_data = load_json_from_file(file_path)

    # Get the human-readable output from GPT-4
    readable_output = query_openai(json_data)
    print("Formatted Information:\n", readable_output)
