import discord
import openai
import yaml
import os

# Load the config file
config_file = os.getenv('CONFIG_FILE', 'config.yaml')
with open(config_file, 'r') as file:
    config = yaml.safe_load(file)

# Initialize the OpenAI API
openai.api_key = config['openai_api_key']

# Define a rate limit helper class
class RateLimiter:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.last_request_time = 0

    def wait(self):
        now = time.time()
        if now - self.last_request_time < self.rate_limit:
            time.sleep(self.rate_limit - (now - self.last_request_time))
        self.last_request_time = time.time()

# Create an instance of RateLimiter with a rate limit of 1 request per second
rate_limiter = RateLimiter(1.0)

# Create an instance of a Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Define the bot's personality
bot_personality = config['bot_personality']

# Define a helper function to get a response from OpenAI
def get_openai_response(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a {bot_personality} bot."},
                {"role": "user", "content": prompt}
            ]
        )
        # Access the generated text from the response
        return response.choices[0].message.content
    except openai.RateLimitError as e:
        print("Rate limit exceeded. Waiting for cooldown...")
        rate_limiter.wait()
        # Retry the request
        return get_openai_response(prompt)
    except Exception as e:
        # Print the full exception stack trace for debugging
        import traceback
        traceback.print_exc()
        print(f"Error while getting response from OpenAI: {e}")
        return "codes fucked mate."


# Define the event for when the bot has connected to Discord
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

# Define the event for when a message is received
@client.event
async def on_message(message):
    try:
        # Log the message content
        print(f"Received message: {message.content} from {message.author}")

        # Don't let the bot reply to itself
        if message.author == client.user:
            return

        # Check if the message is a reply to the bot's message or if the bot is mentioned
        if (message.reference and message.reference.resolved and message.reference.resolved.author == client.user) or client.user.mentioned_in(message):
            # Generate a prompt for the LLM
            prompt = f"The following is a conversation with a {bot_personality} bot. The bot is helpful, creative, clever, and based. It does not reference its personaility.\n\nHuman: {message.content}\nBot:"

            # Get a response from the LLM
            response = get_openai_response(prompt)

            # Send the response back to the Discord channel
            await message.channel.send(response)
    except Exception as e:
        # Print the full exception stack trace for debugging
        import traceback
        traceback.print_exc()
        print(f'Error in on_message: {e}')

# Run the bot with the token from the config file
try:
    client.run(config['token'])
except Exception as e:
    # Print the full exception stack trace for debugging
    import traceback
    traceback.print_exc()
    print(f"Error while running the bot: {e}")
