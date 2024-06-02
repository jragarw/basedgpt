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
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Define the event for when the bot has connected to Discord
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    try:
        # Don't let the bot reply to itself
        if message.author == client.user:
            return

        # Generate a prompt for the LLM
        prompt = f"The following is a conversation with a {bot_personality} bot. The bot is helpful, creative, clever, and very friendly.\n\nHuman: {message.content}\nBot:"
        
        # Get a response from the LLM
        response = await get_openai_response(prompt)
        
        # Send the response back to the Discord channel
        await message.channel.send(response)
    except Exception as e:
        print(f'Error: {e}')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


# Define the event for when a message is received
@client.event
async def on_message(message):
    # Don't let the bot reply to itself
    if message.author == client.user:
        return

    # Generate a prompt for the LLM
    prompt = f"The following is a conversation with a {bot_personality} bot. The bot is helpful, creative, clever, and very friendly.\n\nHuman: {message.content}\nBot:"
    
    # Get a response from the LLM
    response = await get_openai_response(prompt)
    
    # Send the response back to the Discord channel
    await message.channel.send(response)

# Run the bot with the token from the config file
client.run(config['token'])