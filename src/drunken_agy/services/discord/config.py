import os
import sys
import json
import subprocess
from drunken_agy.core.utils import find_config

DEFAULT_BOT_TOKEN = None
DEFAULT_CHANNEL_ID = None



PERSONA_MAPPING = {
    "principal-engineer": "principal-engineer",
    "principal": "principal-engineer",
    "principle": "principal-engineer",
    "archmage": "principal-engineer",
    "wizard": "principal-engineer",
    
    "devops-engineer": "devops-engineer",
    "devops": "devops-engineer",
    "knight": "devops-engineer",
    
    "laravel-developer": "laravel-developer",
    "laravel": "laravel-developer",
    "alchemist": "laravel-developer",
    
    "qa-engineer": "qa-engineer",
    "qa": "qa-engineer",
    "ranger": "qa-engineer",
    
    "security-engineer": "security-engineer",
    "security": "security-engineer",
    "rogue": "security-engineer",
    
    "voice-ai-specialist": "voice-ai-specialist",
    "voice": "voice-ai-specialist",
    "bard": "voice-ai-specialist",
    
    "agentic-systems-specialist": "agentic-systems-specialist",
    "agentic": "agentic-systems-specialist",
    "summoner": "agentic-systems-specialist",
    
    "fullstack-engineer": "fullstack-engineer",
    "fullstack": "fullstack-engineer",
    "spellsword": "fullstack-engineer"
}

def save_config(config):
    config_file = find_config('discord_config.json')
    if not config_file:
        config_file = os.path.join(os.getcwd(), '.agents', 'discord_config.json')
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save config file: {e}", file=sys.stderr)

def load_config():
    config = {
        "bot_token": os.environ.get("DISCORD_BOT_TOKEN") or DEFAULT_BOT_TOKEN,
        "channel_id": None
    }
    
    env_channel_id = os.environ.get("DISCORD_CHANNEL_ID")
    if env_channel_id:
        try:
            config["channel_id"] = int(env_channel_id)
        except ValueError:
            pass

    config_file = find_config('discord_config.json')
    if config_file:
        try:
            with open(config_file, "r") as f:
                file_data = json.load(f)
                if "bot_token" in file_data and file_data["bot_token"]:
                    config["bot_token"] = file_data["bot_token"]
                if "channel_id" in file_data and file_data["channel_id"]:
                    config["channel_id"] = int(file_data["channel_id"])
        except Exception as e:
            print(f"Warning: Failed to parse config file: {e}", file=sys.stderr)
            
    if not config["bot_token"] or config["bot_token"] == DEFAULT_BOT_TOKEN:
        DISCORD_URIS = os.environ.get("DISCORD_PASS_URIS", "").split(",") if os.environ.get("DISCORD_PASS_URIS") else [
            "op://Personal/Discord/token",
            "op://Private/Discord/token",
            "op://Personal/Discord/credential",
            "op://Private/Discord/credential"
        ]
        for uri in DISCORD_URIS:
            try:
                res = subprocess.run(["op", "read", uri], capture_output=True, text=True, check=True)
                token = res.stdout.strip()
                if token:
                    config["bot_token"] = token
                    save_config(config)
                    break
            except Exception:
                continue

    if config["channel_id"] is None:
        config["channel_id"] = DEFAULT_CHANNEL_ID

    return config
