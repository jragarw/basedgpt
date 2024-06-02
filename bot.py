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

# Create an instance of a Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Define the bot's personality
bot_personality = config['bot_personality']

# Define a helper function to get a response from OpenAI
async def get_openai_response(prompt):
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a {bot_personality} bot."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        # Print the full exception stack trace for debugging
        import traceback
        traceback.print_exc()
        print(f"Error while getting response from OpenAI: {e}")
        return "Sorry, I couldn't process your request at the moment."

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
            prompt = f"The following is a conversation with a {bot_personality} bot. The bot is helpful, creative, clever, and very friendly.\n\nHuman: {message.content}\nBot:"

            # Get a response from the LLM
            response = await get_openai_response(prompt)

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
