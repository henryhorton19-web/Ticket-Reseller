import requests
from bs4 import BeautifulSoup
import os
import json
from requests.exceptions import RequestException

# ======= MONITORED FATSOMA PAGES =======
URLS = {
    "Milkshake": "https://www.fatsoma.com/p/milkshake",
    "LSE Athletics Union": "https://www.fatsoma.com/p/lseathleticsunion",
    "LSE Welcome": "https://www.fatsoma.com/p/lsewelcome",
    "LSE Students' Union": "https://www.fatsoma.com/p/lsestudentsunion",
    "Students' Union UCL": "https://www.fatsoma.com/p/studentsunionucl"
}

# ======= KEYWORDS TO TRACK =======
KEYWORDS = [
    "early bird", "1st release", "first release", "sold out"
]

STATE_FILE = 'page_state.json'
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ======= TELEGRAM ALERT SENDER =======
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Missing Telegram credentials.")
        return

    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        print("📨 Telegram status:", response.status_code)
        print("📨 Telegram response:", response.text)
        if response.status_code != 200:
            print("❌ Telegram send failed.")
    except Exception as e:
        print("❌ Exception sending Telegram message:", str(e))

# ======= SCRAPE PAGE CONTENT =======
def fetch_keywords(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        text = BeautifulSoup(response.text, 'html.parser').get_text().lower()
        return {kw: (kw in text) for kw in KEYWORDS}
    except RequestException as e:
        print(f"⚠️ Skipping {url}: {e}")
        return {kw: False for kw in KEYWORDS}

# ======= LOAD / SAVE STATE =======
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

# ======= MAIN CHECKING LOGIC =======
def main():
    previous = load_state()
    current = {}

    # ✅ Manual test alert to confirm it's working
    send_telegram("🧪 *Test Alert:* Your Fatsoma ticket monitor is running successfully.")

    for name, url in URLS.items():
        print(f"🔍 Checking: {name}")
        matches = fetch_keywords(url)
        current[name] = matches

        for keyword, found in matches.items():
            prev = previous.get(name, {}).get(keyword, False)

            # ✅ If keyword appears (new drop)
            if found and not prev:
                if keyword == "sold out":
                    send_telegram(f"❌ *{keyword.title()}* just appeared on *{name}* — event likely full.\n{url}")
                else:
                    send_telegram(f"🎫 *{keyword.title()}* just dropped on *{name}*!\n{url}")

            # ✅ If "sold out" disappears (restock)
            elif not found and prev and keyword == "sold out":
                send_telegram(f"🎉 *Sold Out disappeared* from *{name}* — tickets may be available again!\n{url}")

    save_state(current)

if __name__ == "__main__":
    main()
