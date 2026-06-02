"""
UTON — Telegram AI agent for Mega-AI.CO
===================================================
Platform  : Telegram
AI Brain  : Google Gemini (google-genai)
Config    : .env (python-dotenv)

Run:
    python app.py
"""

import os
import logging
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types as genai_types
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ─────────────────────────────────────────────
# 1.  Load .env
# ─────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ── Your contact info (edit these) ────────────
OWNER_EMAIL    = os.getenv("OWNER_EMAIL",    "your@email.com")
OWNER_WHATSAPP = os.getenv("OWNER_WHATSAPP", "+880XXXXXXXXXX")

if not GEMINI_API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY missing from .env!")
if not TELEGRAM_BOT_TOKEN:
    raise EnvironmentError("❌ TELEGRAM_BOT_TOKEN missing from .env!")

# ─────────────────────────────────────────────
# 2.  Logging
# ─────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 3.  Uton System Prompt
# ─────────────────────────────────────────────

UTON_SYSTEM_PROMPT = f"""
You are Uton, a professional AI sales and support agent for Mega-AI.CO — an AI automation agency.

LANGUAGE RULE:
- ALWAYS reply in English only, no matter what language the customer writes in.

YOUR PERSONALITY:
- Professional, friendly, and confident.
- Keep replies concise and clear (this is a Telegram chat).
- Never say you are an AI or Gemini. You are Uton.

ABOUT MEGA-AI.CO SERVICES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Chatbots          — Custom chatbots for businesses (WhatsApp, Telegram, Web)
⚙️  Workflow Automation  — Automate repetitive tasks using AI (n8n, Make, Zapier)
📊 Data Automation      — Scraping, processing, and reporting with AI
📧 Email Automation     — AI-powered email sequences and follow-ups
🧠 AI Agents            — Custom AI agents for sales, support, and operations
🔗 API Integrations     — Connect any tool or platform with AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO HANDLE CUSTOMERS:
1. Greet them warmly and ask what kind of automation they need.
2. Understand their business problem clearly.
3. Suggest the best service from our list above.
4. If they want to move forward or need a custom quote, tell them:
   → Our team will reach out via email or WhatsApp.
   → Ask for their name and email to proceed.
5. Once they give their name + email, confirm it and say the owner will contact them soon.

CONTACT INFO (give this when customer asks to get in touch):
📧 Email    : {OWNER_EMAIL}
📱 WhatsApp : {OWNER_WHATSAPP}

IMPORTANT RULES:
- Never make up prices. Say "pricing depends on the project scope, our team will give you a custom quote."
- If a customer is ready to hire, collect: their Name + Email.
- Always end with a helpful follow-up question to keep the conversation going.
- Be a great salesperson — highlight the value of automation for their business.
"""

# ─────────────────────────────────────────────
# 4.  Gemini Client
# ─────────────────────────────────────────────

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────
# 5.  Session Store
# ─────────────────────────────────────────────

user_sessions: dict[int, list[dict]] = {}
MAX_HISTORY = 20


def get_session(user_id: int) -> list[dict]:
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    return user_sessions[user_id]


def trim_history(history: list[dict]) -> list[dict]:
    return history[-MAX_HISTORY:] if len(history) > MAX_HISTORY else history


# ─────────────────────────────────────────────
# 6.  AI Response Generator
# ─────────────────────────────────────────────

def generate_uton_response(user_id: int, user_message: str) -> str:
    history = get_session(user_id)

    history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    history = trim_history(history)
    user_sessions[user_id] = history

    try:
        response = gemini_client.models.generate_content(
            model= "gemini-2.5-flash",
            contents=history,
            config=genai_types.GenerateContentConfig(
                system_instruction=UTON_SYSTEM_PROMPT,
                max_output_tokens=450,                               
                temperature=0.7,
            ),
        )
        reply_text = response.text.strip()

    except Exception as exc:
        log.error(f"Gemini Error: {exc}")
        reply_text = (
            f"Sorry, I'm having a connection issue right now. 🙏\n\n"
            f"Please reach out directly:\n"
            f"📧 Email: {OWNER_EMAIL}\n"
            f"📱 WhatsApp: {OWNER_WHATSAPP}"
        )

    history.append({
        "role": "model",
        "parts": [{"text": reply_text}]
    })
    user_sessions[user_id] = history
    return reply_text


# ─────────────────────────────────────────────
# 7.  Telegram Handlers
# ─────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = []  # fresh session

    greeting = (
        "👋 *Welcome to Mega-AI.CO!*\n\n"
        "I'm *Uton*, your AI automation consultant.\n\n"
        "We help businesses save time and grow faster using:\n"
        "🤖 AI Chatbots\n"
        "⚙️ Workflow Automation\n"
        "🧠 Custom AI Agents\n"
        "📧 Email Automation & more\n\n"
        "Tell me — *what does your business do?* "
        "I'll show you exactly how AI can help you. 🚀"
    )
    await update.message.reply_text(greeting, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = []
    await update.message.reply_text("✅ Conversation reset! Type anything to start fresh.")


async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_msg = (
        "📬 *Get In Touch With Us*\n\n"
        f"📧 Email    : `{OWNER_EMAIL}`\n"
        f"📱 WhatsApp : `{OWNER_WHATSAPP}`\n\n"
        "Our team typically responds within a few hours. "
        "We'd love to discuss your automation needs! 🤝"
    )
    await update.message.reply_text(contact_msg, parse_mode="Markdown")


async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services_msg = (
        "⚡ *Mega-AI.CO Services*\n\n"
        "🤖 *AI Chatbots* — WhatsApp, Telegram, Web\n"
        "⚙️ *Workflow Automation* — n8n, Make, Zapier\n"
        "📊 *Data Automation* — Scraping & reporting\n"
        "📧 *Email Automation* — AI-powered sequences\n"
        "🧠 *Custom AI Agents* — Sales, support, ops\n"
        "🔗 *API Integrations* — Connect any platform\n\n"
        "💬 Tell me your business problem and I'll suggest the best solution!"
    )
    await update.message.reply_text(services_msg, parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id   = update.effective_user.id
    user_name = update.effective_user.first_name or "there"
    user_msg  = update.message.text.strip()

    log.info(f"📩 [{user_id} | {user_name}]: {user_msg}")

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    reply = generate_uton_response(user_id, user_msg)

    log.info(f"🤖 [Uton → {user_name}]: {reply}")
    await update.message.reply_text(reply)


# ─────────────────────────────────────────────
# 8.  Entry Point
# ─────────────────────────────────────────────

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 UTON — Mega-AI.CO Telegram Bot")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Owner Email    : {OWNER_EMAIL}")
    print(f"  Owner WhatsApp : {OWNER_WHATSAPP}")
    print(f"  Gemini Model   : gemini-2.5-flash")
    print("  Status         : Online ✅")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    start_command))
    app.add_handler(CommandHandler("reset",    reset_command))
    app.add_handler(CommandHandler("contact",  contact_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()