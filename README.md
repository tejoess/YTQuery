# 🤖 YTQuery

**YTQuery** is an intelligent chatbot that lets you interact with YouTube videos like never before. Simply paste a video link and start asking questions — YTQuery watches, understands, and responds with clear, concise answers based on the video's content using the power of **Google Gemini**.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** Flask
* **AI Engine:** Google Gemini API
* **Deployment:** Render (via `render.yaml`)

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone [https://github.com/tejoess/YTQuery.git](https://github.com/tejoess/YTQuery.git)
cd YTQuery
```
2. Set up Environment Variables
Create a .env file in the root directory and add your API key:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Run the App
```bash
python app.py
```

📂 File Overview
app.py: The Flask web server that handles routing.

ytchatbot.py: Contains the logic for interacting with the Gemini API.

templates/: Holds the HTML files for the chatbot interface.

render.yaml: Configuration for easy deployment to Render.com.
