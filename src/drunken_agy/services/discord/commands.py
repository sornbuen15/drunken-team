import os
import asyncio
import discord
from drunken_agy.services.discord import state
from drunken_agy.services.discord.utils import log_activity, extract_clean_response

async def run_command_async(channel, user_mention, command_content, full_cmd, agent_name):
    # Send immediate acknowledgement as Mina
    status_msg = await channel.send(
        f"🎯 **Quest order received, Boss!** 🍺\n"
        f"Mina has dispatched the quest order to **{agent_name}** in the backroom office.\n"
        f"I'll bring the report straight to your table once completed!\n"
        f"⏳ **Status:** Processing behind the scenes... *(You can click ❌ to cancel the order anytime, Boss)*"
    )
    try:
        await status_msg.add_reaction("❌")
    except Exception:
        pass
        
    state.current_status_msg = status_msg
    state.is_cancelled = False
    
    try:
        log_redirect_cmd = f"{full_cmd} > {state.RAW_LOG_FILE} 2>&1"
        process = await asyncio.create_subprocess_shell(
            log_redirect_cmd,
            stdin=asyncio.subprocess.DEVNULL
        )
        state.current_process = process
        await process.wait()
    except Exception as e:
        with open(state.RAW_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\nError executing command: {e}\n")
        log_activity("agent", "Agent", f"Failed: {e}")
        await status_msg.edit(
            content=f"⚠️ **Oh no, Boss!** The quest order for **{agent_name}** failed to start:\n`{e}`"
        )
        try:
            await status_msg.clear_reactions()
        except Exception:
            pass
        return

    state.current_process = None
    state.current_status_msg = None

    if state.is_cancelled:
        log_activity("agent", "Agent", "Task cancelled by user.")
        await status_msg.edit(
            content=f"🛑 **Order cancelled, Boss!**\n🏁 **Status:** Aborted by the Boss."
        )
        try:
            await status_msg.clear_reactions()
        except Exception:
            pass
        state.is_cancelled = False
        return

    clean_resp = ""
    if os.path.exists(state.RAW_LOG_FILE):
        try:
            with open(state.RAW_LOG_FILE, "r", encoding="utf-8") as f:
                raw_log = f.read()
                clean_resp = extract_clean_response(raw_log)
        except Exception:
            pass

    try:
        await status_msg.clear_reactions()
    except Exception:
        pass

    await status_msg.edit(
        content=f"🎯 **Quest completed, Boss!**\n🏁 **Status:** Finished! The report is served at your table."
    )

    if clean_resp:
        log_activity("agent", "Agent", clean_resp)
        formatted_content = f"🛎️ **Boss! The report is served!** ({user_mention})\n\n{clean_resp}"
        if len(formatted_content) > 1950:
            formatted_content = formatted_content[:1950] + "...\n*(Content too long. Type !detail to upload the full raw log file)*"
        await channel.send(formatted_content)
    else:
        log_activity("agent", "Agent", "Completed.")
        await channel.send(
            f"🛎️ **Boss! The report is served!** ({user_mention})\n🏁 **Status:** Completed. *(Type !detail to check execution logs)*"
        )
