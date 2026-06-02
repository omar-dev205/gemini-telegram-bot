AI Telegram Bot (Powered by Google Gemini)
This is a smart, intelligent Telegram bot integrated with the Google Gemini API. It is designed to provide real-time, conversational responses, automating interactions with ease and efficiency.

Features
AI-Powered Responses: Uses Google Gemini to generate human-like, intelligent chat responses.

Asynchronous Processing: Built with python-telegram-bot for smooth and non-blocking performance.

Secure Configuration: Uses environment variables (.env) for secure management of API keys and tokens.

Easy to Deploy: Lightweight structure, easy to run on local machines or servers.

Prerequisites
Before running the bot, ensure you have the following installed:

Python 3.10+

Telegram Bot Token (obtained from BotFather)

Google Gemini API Key (obtained from Google AI Studio)

Installation
Clone the repository:

Bash
git clone https://github.com/omar-dev205/gemini-telegram-bot.git
cd gemini-telegram-bot

2.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
Setup environment variables:
Create a file named .env in the root directory and add your credentials:

Plaintext
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

4.  **Run the bot:**
    ```bash
    python agent.py
License
This project is licensed under the MIT License.
