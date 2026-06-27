import os
import json
import asyncio
import discord
import re
from drunken_agy.services.discord import state
from drunken_agy.services.discord.config import config
from drunken_agy.core.agents import AGENTS_METADATA
from drunken_agy.services.discord.utils import log_activity
from drunken_agy.services.discord.commands import run_command_async
from drunken_agy.services.discord.gemini import query_gemini_direct
from drunken_agy.core.utils import find_config

def setup_events(client):
    
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user.name}", flush=True)
        asyncio.create_task(poll_outbox(client))

    async def poll_outbox(client):
        outbox_file = os.path.join(os.getcwd(), '.agents', 'discord_outbox.json')
        inbox_file = os.path.join(os.getcwd(), '.agents', 'discord_inbox.json')
        
        channel = client.get_channel(config["channel_id"])
        if not channel:
            try:
                channel = await client.fetch_channel(config["channel_id"])
            except Exception:
                return
                
        while True:
            try:
                if os.path.exists(outbox_file):
                    with open(outbox_file, 'r') as f:
                        outbox = json.load(f)
                    
                    if outbox:
                        with open(outbox_file, 'w') as f:
                            json.dump({}, f)
                            
                        for req_id, data in outbox.items():
                            question = data.get('question')
                            
                            msg = await channel.send(question)
                            await msg.add_reaction("👍")
                            await msg.add_reaction("👎")
                            await msg.add_reaction("🌟")
                            
                            asyncio.create_task(wait_for_boss_reaction(client, msg, req_id, inbox_file))
            except Exception:
                pass
                
            await asyncio.sleep(1)

    async def wait_for_boss_reaction(client, msg, req_id, inbox_file):
        def check(reaction, user):
            if user.id == client.user.id: return False
            if reaction.message.id != msg.id: return False
            if str(reaction.emoji) not in ["👍", "👎", "🌟"]: return False
            if msg.guild and user.id == msg.guild.owner_id: return True
            elif not msg.guild: return True
            return False
            
        try:
            reaction, user = await client.wait_for('reaction_add', check=check)
            status = "rejected"
            if str(reaction.emoji) == "👍": status = "approved"
            elif str(reaction.emoji) == "🌟": status = "approved_always"
            
            inbox = {}
            if os.path.exists(inbox_file):
                try:
                    with open(inbox_file, 'r') as f: inbox = json.load(f)
                except Exception: pass
                
            inbox[req_id] = {"status": status}
            with open(inbox_file, 'w') as f:
                json.dump(inbox, f)
                
        except Exception:
            pass

    @client.event
    async def on_reaction_add(reaction, user):
        if user.id == client.user.id:
            return
            
        if str(reaction.emoji) == "❌":
            if state.current_status_msg and reaction.message.id == state.current_status_msg.id:
                if state.current_process and state.current_process.returncode is None:
                    try:
                        print(f"[Debug] Terminating running task due to ❌ reaction by {user.name}", flush=True)
                        state.is_cancelled = True
                        state.current_process.terminate()
                        await asyncio.sleep(1)
                        if state.current_process.returncode is None:
                            state.current_process.kill()
                    except Exception as e:
                        print(f"Error terminating task: {e}", flush=True)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        print(f"[Debug] Received message in channel {message.channel.id} (Configured: {config['channel_id']}) from {message.author}: {message.content[:50]}", flush=True)

        if message.channel.id != config["channel_id"]:
            return

        log_activity("user", message.author.name, message.content.strip())

        content_str = message.content.strip()
        if not content_str:
            return

        if content_str == "!detail":
            if os.path.exists(state.RAW_LOG_FILE) and os.path.getsize(state.RAW_LOG_FILE) > 0:
                try:
                    await message.channel.send(
                        content="Here is the raw execution log file, Boss:",
                        file=discord.File(state.RAW_LOG_FILE)
                    )
                except Exception as e:
                    await message.channel.send(f"Mina failed to upload raw log file due to error: {e}")
            else:
                await message.channel.send("No raw execution history found in the tavern logbook, Boss.")
            return

        if content_str.startswith("/"):
            parts = content_str.split(None, 1)
            slash_cmd = parts[0].lower()
            args_str = parts[1] if len(parts) > 1 else ""

            if slash_cmd == "/help":
                help_text = (
                    "Hello, Boss! 🍺 Mina, your tavern hostess, welcomes you to the **Drunken AGY Inn**!\n"
                    "I coordinate tasks in the backroom office so you don't have to wait. Grab a pint of ale and relax!\n\n"
                    "**How to order quests:**\n"
                    "1. **Quick Slash Commands:**\n"
                    "   - `/help` : Show this help menu.\n"
                    "   - `/list-cmd` : View list of fast executable system commands.\n"
                    "   - `/refine` : Refine and clean up Jira backlog.\n"
                    "   - `/next` : Pull and start the next highest priority task.\n"
                    "   - `/audit` : Audit codebase architecture and technical debt.\n"
                    "   - `/confluence-sync` : Sync ADRs/Specs to Confluence Cloud.\n\n"
                    "2. **Ask/Direct Quest Agents (Async):**\n"
                    "   Type in format: `<who> <context> <goal>`\n"
                    "   *Example:* `principal project-tff refine backlog`\n"
                    "   *Tavern Agents Roster (aliases):*\n"
                    "   - `principal` (🧙‍♂️ Archmage - Architecture & Rules)\n"
                    "   - `devops` (🛡️ Iron Knight - Infrastructure & Pipeline)\n"
                    "   - `laravel` (🧪 Alchemist - PHP & Laravel Core)\n"
                    "   - `qa` (🏹 Ranger - Bug Hunting & Test Suite)\n"
                    "   - `security` (👤 Rogue - Security Audit & Vulnerabilities)\n"
                    "   - `voice` (🎵 Bard - AI Voice & WebRTC)\n"
                    "   - `agentic` (🌀 Summoner - Multi-agent setup)\n"
                    "   - `fullstack` (⚔️ Spellsword - Frontend/Backend/CSS)\n\n"
                    "Mina is always waiting for your order at the counter! 🍹"
                )
                await message.channel.send(help_text)
                return

            elif slash_cmd == "/list-cmd":
                list_text = (
                    "Boss! Here is the menu of quick commands that I can relay to the agy CLI immediately:\n"
                    "1. `/refine` : Run JIRA Backlog refinement.\n"
                    "2. `/next` : Pull and start the highest priority task.\n"
                    "3. `/audit` : Run codebase health audit and trace technical debt.\n"
                    "4. `/confluence-sync` : Sync documentation files to Confluence Cloud.\n\n"
                    "You can type `/<command>` to execute it immediately!"
                )
                await message.channel.send(list_text)
                return

            mapped_cmd = slash_cmd.lstrip("/")
            cli_mapping = {
                "refine": "/refine",
                "next": "/next",
                "audit": "/audit",
                "confluence-sync": "/confluence-sync"
            }
            
            agy_cmd = cli_mapping.get(mapped_cmd, content_str)
            full_cmd = f'agy --dangerously-skip-permissions --print "{agy_cmd}"'
            
            asyncio.create_task(run_command_async(
                message.channel, 
                message.author.mention, 
                content_str, 
                full_cmd, 
                "System Agent"
            ))
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            router_instruction = (
                "You are Mina, the lively and welcoming tavern hostess at the Drunken AGY Inn.\n"
                "You coordinate dashboard and quest orders for The Boss.\n"
                "The available developer agents are:\n"
                "- principal-engineer: ARCHMAGE (Alias: Principal/Wizard). Role: Architecture, rules, Jira\n"
                "- devops-engineer: KNIGHT (Alias: DevOps). Role: Infrastructure, K8s\n"
                "- laravel-developer: ALCHEMIST (Alias: Laravel). Role: PHP, DB\n"
                "- qa-engineer: RANGER (Alias: QA). Role: Testing\n"
                "- security-engineer: ROGUE (Alias: Security). Role: Security\n"
                "- voice-ai-specialist: BARD (Alias: Voice/Audio). Role: Voice/WebRTC\n"
                "- agentic-systems-specialist: SUMMONER (Alias: Agentic). Role: Multi-agent\n"
                "- fullstack-engineer: BLADE (Alias: Fullstack/Spellsword). Role: Frontend/UI/CSS\n\n"
                "Return a JSON object ONLY, no markdown formatting outside of it:\n"
                "If it's a casual chat or general question that you can answer without running terminal commands, return:\n"
                '{"is_task": false, "mina_response": "<Your friendly in-character response addressing The Boss>"}\n'
                "If it's a technical task, code modification, debugging, or explicitly assigning an agent by name/alias, return:\n"
                '{"is_task": true, "target_agent": "<best_agent_key>", "refined_prompt": "<clear prompt for the agent>"}'
            )
            
            direct_response = await asyncio.to_thread(query_gemini_direct, content_str, router_instruction)
            
            if direct_response:
                try:
                    clean_json = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', direct_response, flags=re.DOTALL).strip()
                    router_data = json.loads(clean_json)
                except Exception as e:
                    router_data = {"is_task": False, "mina_response": direct_response}
                    
                if not router_data.get("is_task"):
                    resp = router_data.get("mina_response", direct_response)
                    log_activity("agent", "Mina", resp)
                    await message.channel.send(f"🍹 **Mina [Hostess]:** {resp}")
                    return
                
                target_agent = router_data.get("target_agent", "fullstack-engineer")
                if target_agent not in AGENTS_METADATA:
                    target_agent = "fullstack-engineer"
                    
                agent_meta = AGENTS_METADATA[target_agent]
                refined_prompt = router_data.get("refined_prompt", content_str)
                
                config_file = find_config('discord_config.json')
                if config_file:
                    active_agent_json = os.path.join(os.path.dirname(config_file), "active_agent.json")
                    try:
                        with open(active_agent_json, "w") as f:
                            json.dump({"active_agent": target_agent}, f)
                    except Exception:
                        pass
                
                suffix = (
                    f"\n\n(Instructions: You are {agent_meta['name']} [Job: {agent_meta['job']}]. "
                    f"Personality: {agent_meta['description']}. "
                    "Respond like a human software developer in character. "
                    "Address the user as 'The Boss'. "
                    "Be extremely brief, conversational, and direct. Explain in 1-2 short sentences "
                    "exactly what you did. Do not use AI clichés or preamble. Start directly.)"
                )
                escaped_prompt = (refined_prompt + suffix).replace('"', '\\"')
                full_cmd = f'agy --dangerously-skip-permissions --print "{escaped_prompt}"'

                asyncio.create_task(run_command_async(
                    message.channel, 
                    message.author.mention, 
                    refined_prompt, 
                    full_cmd, 
                    agent_meta['name']
                ))
                return

        welcoming_text = (
            f"Hello, Boss! 🍹 refreshing Mina, your tavern hostess, welcomes you to the Drunken AGY Inn!\n"
            f"I coordinate dashboard and quest orders in the tavern. Would you like to run a quick command or assign a quest to an agent?\n\n"
            f"💡 *Quick Tip:* Type `/help` to see instructions, or try the format `<who> <context> <goal>` such as: \n"
            f"`principal project-tff refine backlog` to deploy the principal engineer immediately!"
        )
        await message.channel.send(welcoming_text)
