from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

KOZJOL_CHAT_ID = -1002075990685

SUPPORTED_FOODS = ["🍗", "🐟", "🥓", "🍕", "🥛", "🧀", "🥩", "🍖", "🍤"]

GAMES = {"Mouse catch game":"play_mouse"}