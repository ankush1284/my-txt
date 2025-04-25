import os

# Telegram 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
DATABASE_URI = os.getenv("DATABASE_URI")

# Conversation States
LOGIN, COURSE_SELECTION = range(2)

# Website URLs
BASE_URL = 'https://app.khanglobalstudies.com'
LOGIN_URL = f'{BASE_URL}/login'
DASHBOARD_URL = f'{BASE_URL}/dashboard'
