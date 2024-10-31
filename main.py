import os
import time
from flask import Flask, request, jsonify
import openai
from openai import OpenAI

# Set your OpenAI API key and the Assistant ID you want to use
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
ASSISTANT_ID = "asst_v2pbJtHtFN9mcZYSC1cDDymU" 
app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)
assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
print(f"Using Assistant: {assistant.id}")

# Start conversation thread
@app.route('/start', methods=['GET'])
def start_conversation():
    print("Starting a new conversation...")
    thread = client.beta.threads.create(
      tool_resources={
        "file_search": {
          "vector_store_ids": ["vs_B6hcEBIg0B3fYTlcZtlVNguU"]
        }
      }
    )
    print(f"New thread created with ID: {thread.id}")
    return jsonify({"thread_id": thread.id})

# Generate response
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
        print("Error: Missing thread_id")
        return jsonify({"error": "Missing thread_id"}), 400

    print(f"Received message: {user_input} for thread ID: {thread_id}")

    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=user_input)

    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.id)

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print('Run Status:', run.status)
        time.sleep(1)
    else:
        print('Run Completed')

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
