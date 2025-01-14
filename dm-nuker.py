import subprocess
import sys

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("requests")

import requests
import json
import time

BASE_URL = "https://discord.com/api/v9"

def get_token():
    print("=" * 30)
    print("Discord DM Nuker")
    print("=" * 30)
    token = input("Enter your Discord token: ").strip()
    return token

def get_dm_channels(headers):
    try:
        response = requests.get(f"{BASE_URL}/users/@me/channels", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching DM channels: {e}")
        return []

def fetch_messages(channel_id, user_id, headers):
    my_messages = []
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    params = {"limit": 100}
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            batch = response.json()
            if not batch:
                break
            for msg in batch:
                if msg["author"]["id"] == user_id:
                    my_messages.append(msg["id"])
            params["before"] = batch[-1]["id"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages from channel {channel_id}: {e}")
    return my_messages

def delete_message(channel_id, message_id, headers):
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Message {message_id} deleted successfully.")
        else:
            print(f"Failed to delete message {message_id}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting message {message_id}: {e}")

def main():
    token = get_token()
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    user_response = requests.get(f"{BASE_URL}/users/@me", headers=headers)
    if user_response.status_code != 200:
        print("Failed to fetch user details.")
        return
    user_data = user_response.json()
    username = user_data.get("username", "Unknown User")
    print(f"Logged in as: {username}")
    dm_channels = get_dm_channels(headers)
    if not dm_channels:
        return
    user_id = user_data["id"]
    for channel in dm_channels:
        if channel["type"] == 1:
            recipient = channel["recipients"][0]
            recipient_username = recipient.get("username", "unknown_user")
            print(f"Processing messages from DM with {recipient_username}")
            my_messages = fetch_messages(channel["id"], user_id, headers)
            for msg in my_messages:
                delete_message(channel["id"], msg, headers)
                time.sleep(1)

if __name__ == "__main__":
    main()
