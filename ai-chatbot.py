import subprocess
import sys

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("google-generativeai")
install_package("requests")

import requests
import time
import google.generativeai as genai

BASE_URL = "https://discord.com/api/v9"

def get_token_and_keys():
    print("=" * 30)
    print("Discord Bot with Google Generative AI")
    print("=" * 30)
    token = input("Enter your Discord token: ").strip()
    api_key = input("Enter your Gemini API key: ").strip()
    server_id = input("Enter the Discord server ID: ").strip()
    channel_id = input("Enter the Discord channel ID: ").strip()
    return token, api_key, server_id, channel_id

def fetch_latest_message(channel_id, headers):
    url = f"{BASE_URL}/channels/{channel_id}/messages?limit=1"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        messages = response.json()
        return messages[0] if messages else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages from channel {channel_id}: {e}")
        return None

def send_message(channel_id, content, reply_to_message_id, headers):
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    payload = {
        "content": content,
        "message_reference": {
            "message_id": reply_to_message_id
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Reply sent successfully.")
        else:
            print(f"Failed to send reply: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending reply: {e}")

def generate_response(api_key, prompt):
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response with GenAI: {e}")
        return "I couldn't process your request."

def main():
    token, api_key, _, channel_id = get_token_and_keys()
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

    print(f"Listening to messages in channel: {channel_id}")
    last_processed_message_id = None
    while True:
        latest_message = fetch_latest_message(channel_id, headers)
        if latest_message:
            message_id = latest_message["id"]
            author_id = latest_message["author"]["id"]
            content = latest_message.get("content", "")

            if message_id != last_processed_message_id and author_id != user_data["id"]:
                print(f"Received message: {content}")
                response_message = generate_response(api_key, content)
                send_message(channel_id, response_message, message_id, headers)
                last_processed_message_id = message_id

        time.sleep(2)

if __name__ == "__main__":
    main()
