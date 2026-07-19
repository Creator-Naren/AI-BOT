from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# OpenRouter configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using a public LibreTranslate mirror (fallback to original text if down)
TRANSLATE_URL = "https://translate.argosopentech.com"

def detect_language(text):
    try:
        res = requests.post(f"{TRANSLATE_URL}/detect", data={"q": text}, timeout=3)
        if res.ok and len(res.json()) > 0:
            return res.json()[0].get("language", "en")
    except Exception as e:
        print("Lang detect error:", e)
    return "en"

def translate_text(text, source="auto", target="en"):
    try:
        res = requests.post(f"{TRANSLATE_URL}/translate", data={
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }, timeout=5)
        if res.ok:
            return res.json().get("translatedText", text)
    except Exception as e:
        print("Translation error:", e)
    return text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    try:
        # Detect language of the latest user message
        user_msg = messages[-1]["content"]
        original_lang = detect_language(user_msg)
        
        # Translate to English for the LLM if not English
        if original_lang != "en":
            translated_user_msg = translate_text(user_msg, source=original_lang, target="en")
            messages[-1]["content"] = translated_user_msg

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct",
            "messages": messages
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        bot_message = response_data['choices'][0]['message']['content']
        
        # Translate the bot's response back to original language
        if original_lang != "en":
            bot_message = translate_text(bot_message, source="en", target=original_lang)
            
        return jsonify({"message": bot_message, "lang": original_lang})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get response from AI: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
