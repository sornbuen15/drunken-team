import sys
import discord
from drunken_agy.services.discord.config import config
from drunken_agy.services.discord.events import setup_events

def main():
    if not config["bot_token"]:
        print("Error: Missing Discord Bot Token. Please set DISCORD_BOT_TOKEN in env or configure it.", file=sys.stderr)
        sys.exit(1)

    if not config["channel_id"]:
        print("Error: Missing Discord Channel ID. Please set DISCORD_CHANNEL_ID in env or configure it.", file=sys.stderr)
        sys.exit(1)

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    setup_events(client)
    
    try:
        client.run(config["bot_token"])
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
