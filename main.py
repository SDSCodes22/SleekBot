import discord
from dotenv import dotenv_values
import json
import vertexai
from vertexai.generative_models import Part, Content, GenerativeModel
from os import path
import random

# Read token from local .env file
TOKEN = dotenv_values(".env")["TOKEN"]
# Initialize ChatGPT
# The project is the Google Cloud Project Name
print("Initializing Vertex AI!")
vertexai.init(project="sleek-bot", location="europe-west2")
model = GenerativeModel("gemini-1.0-pro")
print("...\tDone!")
FIXED_PROMPT = """
Take the following phrase and change it such that it sounds like an extremely posh person is saying it. Use as many complicated words and phrases as possible. Make the output longer than the input. Your response should be in JSON format, with one key-value pair ONLY. The key should be "message" and the value of it should be the output, "fancified" version of the phrase.

This is the phrase:
"""

# intents time!
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("$sleek") or message.content.startswith("$yap"):
        print(f"Final Message:{message.content[7:]}")
        msg = FIXED_PROMPT + message.content[7:]
        # Generating a response
        response = model.generate_content(
            contents=[
                Content(
                    role="user",
                    parts=[
                        Part.from_text(msg),
                    ],
                )
            ]
        )
        print(f"Received response from Gemini.")
        final = response.text.replace("`", "")
        final = final.replace("json", "")
        try:
            final = json.loads(final)
            final = final["message"]
        except Exception as e:
            print(
                f"Gemini sent response in wrong format.\nReponse:\n{final}\n\nError:\n{e}"
            )

        # Get the user's name and profile pic
        name = message.author.nick
        avatar_url = message.author.avatar.url

        # Get all the webhooks in this channel
        webhooks = await message.channel.webhooks()
        # Make sure the webhooks belong to us
        webhooks = [
            i for i in webhooks if i.user == bot.user
        ]  # TODO: bot.user could also be guild.me
        print(f"webhooks: {webhooks}")
        webhook = None
        if len(webhooks) == 0:
            webhook = await message.channel.create_webhook(
                name="TEMP_WEBHOOK_YAP",
                reason="This webhook is required for SleekBot to imitate users",
            )
        else:
            webhook = webhooks[0]
        # Now send the message
        await webhook.send(content=final, username=name, avatar_url=avatar_url)
        await message.delete()


@bot.slash_command(guild_ids=[1212810116647362640])
async def rizz(ctx, private=True):
    # Load all rizz lines
    rizz_lines = []
    file_path = path.join(path.dirname(__file__), "rizz_lines.txt")
    with open(file_path, mode="r") as rizz_file:
        rizz_lines = rizz_file.readlines()
    # Send one to the user
    await ctx.send_response(content=random.choice(rizz_lines), ephemeral=private)


@bot.slash_command(guild_ids=[1212810116647362640])
async def ping(ctx):
    await ctx.send_response(content="pong!", ephemeral=True)


bot.run(TOKEN)
