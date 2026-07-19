<div align="center">
# 🤖 Nova AI Assistant
A modern, lightning-fast, and multilingual AI Chatbot Web Application powered by Flask, Vanilla JS, OpenRouter (Llama 3.1), and LibreTranslate. 
<img src="./demo.png" alt="Nova AI Chatbot Interface" width="800"/>
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Llama 3](https://img.shields.io/badge/Model-Llama_3.1_8B-orange.svg)](https://ai.meta.com/llama/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>
---
## 🌟 Overview
**Nova AI** is an advanced AI assistant web application that brings premium design, high-speed inference, and seamless language translation into a single package. Designed with a sleek glassmorphism dark theme, Nova uses the highly capable **Llama-3.1-8B-Instruct** model under the hood to answer complex queries, assist with coding, summarize data, and more.
### ✨ Key Features
- **⚡ Lightning-Fast Inference**: Utilizes Llama 3.1 via OpenRouter for blazing-fast responses and advanced reasoning.
- **🌍 Real-Time Translation**: Integrated with **LibreTranslate**. Nova automatically detects your language, translates it to English for processing to maximize LLM reasoning, and translates the response back to your native language seamlessly.
- **🎨 Premium UI/UX**: 
  - Dynamic Dark / Light theme toggling
  - Smooth micro-animations (slide-in messages, bouncing typing indicators)
  - Beautiful markdown formatting for code blocks and rich text
- **💾 Persistent History**: Your chat history is saved locally in your browser and persists across page reloads.
---
## 🚀 Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.
### Prerequisites
You will need Python 3.8+ installed on your system.
### Installation
1. **Clone the repository** (if applicable) or download the source code:
   ```bash
   git clone https://github.com/yourusername/ai-chatbot.git
   cd ai-chatbot
   ```
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Flask application**:
   ```bash
   python app.py
   ```
5. **Open your browser** and navigate to:
   ```text
   http://127.0.0.1:5000
   ```
---
## 🛠️ Technology Stack
- **Backend**: [Python](https://www.python.org/) & [Flask](https://flask.palletsprojects.com/)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **APIs**: 
  - **[OpenRouter](https://openrouter.ai/)**: Serving `meta-llama/llama-3.1-8b-instruct`
  - **[LibreTranslate](https://libretranslate.com/)**: Handling language detection and on-the-fly translation.
- **Styling**: Google Fonts (Inter), FontAwesome Icons
---
## 💡 How the Translation Works
Nova is inherently multilingual. Here is the lifecycle of a non-English message:
1. User sends a message in Spanish (`¿Cómo estás?`).
2. Backend detects the language via LibreTranslate (`es`).
3. Backend translates the message to English (`How are you?`) and feeds it to the LLM.
4. Llama 3 responds in English (`I'm doing well, thank you!`).
5. Backend translates the response back to Spanish (`¡Estoy bien, gracias!`) and sends it to the frontend.
6. The UI displays the response with a neat footnote: *(Translated from es via LibreTranslate)*.
---
## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
<div align="center">
  <i>Built with ❤️ by Victu & Nova AI</i>
</div>
