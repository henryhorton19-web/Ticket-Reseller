import requests
from bs4 import BeautifulSoup
import os
import json

URLS = {
    "Fixr UCL Boat Party": "https://fixr.co/event/ucl-boat-party-tickets",
    "Eventbrite Desi Night": "https://www.eventbrite.co.uk/e/desi-night-london-tickets-1234567890",
    "Ministry of Sound Events": "https://www.ministryofsound.com/events",
    "Fatsoma Hideout": "https://www.fatsoma.com/p/hideout-events",
    "Native FM Freshers": "https://native.fm/events",
    "DICE FM London Uni": "https://dice.fm/search?query=university%20london"
}

KEYWORDS = [
    "sold out", "first release", "second release", "final release",
    "tickets live", "limited tickets", "now available", "halloween",
    "freshers", "ball", "boat party", "ministry of sound", "desi night",
    "ucl rave", "early bird", "official afterparty", "ticket drop"
]

STATE_FILE = 'page_state.json'
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials.")
        return
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def fetch_keywords(url):
    try:
        html = requests.get(url, timeout=15).text
        text = BeautifulSoup(html, 'html.parser').get_text().lower()
        return {kw: (kw in text) for kw in KEYWORDS}
    except Exception as e:
        print(f"Error with {url}: {e}")
        return {}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    previous = load_state()
    current = {}
# TEST MODE: Simulate a keyword alert
send_telegram("🧪 Test Alert: Your ticket tracker is working! 🚀")

for name, url in URLS.items():
        print(f"Checking: {name}")
        matches = fetch_keywords(url)
        current[name] = matches

        for keyword, found in matches.items():
            prev = previous.get(name, {}).get(keyword, False)
            if found and not prev:
                send_telegram(f"🔔 '{keyword}' appeared on: {name}\n{url}")
            elif not found and prev and keyword == "sold out":
                send_telegram(f"🎟️ '{keyword}' disappeared (tickets may be available): {name}\n{url}")

    save_state(current)

if __name__ == "__main__":
    main()
