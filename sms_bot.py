import os
from dotenv import load_dotenv
import openai
import plivo
from flask import Flask, request, Response
from plivo import plivoxml

app = Flask(__name__)


load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set Plivo credentials
plivo_auth_id = os.getenv("PLIVO_AUTH_ID")
plivo_auth_token = os.getenv("PLIVO_AUTH_TOKEN")

# Retrieve OpenAI engine from the environment variable
try:
    engine = os.environ["OPENAI_ENGINE"]
except KeyError:
    engine = "gpt-3.5-turbo"

def ask_openai(question):
    response = openai.ChatCompletion.create(
        model=engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering with a short answer not longer than 20 words."},
            {"role": "user", "content": question}
        ]
    )
    answer = response['choices'][0]['message']['content'].strip()
    print("Questiom: {} -> Answer: {}".format(question, answer))
    return answer

@app.route("/sms", methods=["POST"])
def sms_reply():
    # Get the text message sent by the user
    text_message = request.form.get("Text")
    _from = request.form.get("From")
    _to = request.form.get("To")

    # Get the answer from OpenAI
    answer = ask_openai(text_message)

    # Generate Plivo XML response
    response = plivoxml.ResponseElement()
    response.add_message(answer, src=_to, dst=_from)
    return Response(str(response.to_string()), mimetype="application/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

