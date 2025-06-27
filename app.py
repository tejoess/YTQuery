from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from ytchatbot import get_transcript, text_splitting, create_vector_store, create_retriever, create_chat_model
from langchain_core.messages import HumanMessage, AIMessage
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'devsecret')

# Temporary in-memory stores (replace with Redis or DB for production)
TRANSCRIPT_CACHE = {}
VECTOR_STORE_CACHE = {}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/set_video', methods=['POST'])
def set_video():
    yt_link = request.form['yt_link']
    session['yt_link'] = yt_link
    session['history'] = []

    transcript = get_transcript(yt_link)
    if transcript.startswith("Error"):
        return f"<h2>{transcript}</h2>"

    TRANSCRIPT_CACHE[yt_link] = transcript

    chunks = text_splitting(transcript)
    vector_store = create_vector_store(chunks)
    VECTOR_STORE_CACHE[yt_link] = vector_store

    return redirect(url_for('chat'))

@app.route('/chat', methods=['GET'])
def chat():
    yt_link = session.get('yt_link')
    if not yt_link:
        return redirect(url_for('index'))
    return render_template('chat.html', yt_link=yt_link)

@app.route('/chat', methods=['POST'])
def chat_post():
    user_message = request.json['message']
    yt_link = session.get('yt_link')
    history = session.get('history', [])

    if not yt_link or yt_link not in TRANSCRIPT_CACHE:
        return jsonify({'answer': 'No video selected or transcript not found.'})

    transcript = TRANSCRIPT_CACHE[yt_link]
    if not transcript:
        return jsonify({'answer': 'Transcript not available.'})
    vector_store = VECTOR_STORE_CACHE.get(yt_link)
    if not vector_store:
        chunks = text_splitting(transcript)
        vector_store = create_vector_store(chunks)
        VECTOR_STORE_CACHE[yt_link] = vector_store

    results = create_retriever(vector_store, user_message)

    # Build chat history for prompt
    history_msgs = []
    for i, msg in enumerate(history):
        if i % 2 == 0:
            history_msgs.append(HumanMessage(content=msg))
        else:
            history_msgs.append(AIMessage(content=msg))

    response = create_chat_model(results, user_message, history_msgs)

    history.append(user_message)
    history.append(response)
    session['history'] = history[-20:]  # Limit session size

    return jsonify({'answer': response})

@app.route("/")
def home():
    return "Hello from YTQuery!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 locally
    app.run(host="0.0.0.0", port=port)
