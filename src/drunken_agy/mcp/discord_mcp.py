import os
import sys
import json
import uuid
import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("discord-mcp")

def get_agents_dir():
    # Use current directory .agents or traverse up
    curr_dir = os.getcwd()
    while True:
        agents_dir = os.path.join(curr_dir, '.agents')
        if os.path.exists(agents_dir):
            return agents_dir
        parent = os.path.dirname(curr_dir)
        if parent == curr_dir:
            break
        curr_dir = parent
    # Default to .agents in cwd
    default_dir = os.path.join(os.getcwd(), '.agents')
    os.makedirs(default_dir, exist_ok=True)
    return default_dir

@mcp.tool()
def ask_boss(question: str) -> str:
    """
    Ask the Boss for explicit permission, clarification, or approval via Discord.
    This bypasses the terminal UI sandbox by sending the question directly
    through the Discord bot outbox and waiting for a 👍/👎/🌟 reaction from the Boss.
    
    Args:
        question: The question or permission request to ask the Boss.
        
    Returns:
        A string indicating 'approved', 'approved_always', or 'rejected'.
    """
    agents_dir = get_agents_dir()
    outbox_file = os.path.join(agents_dir, 'discord_outbox.json')
    inbox_file = os.path.join(agents_dir, 'discord_inbox.json')
    
    req_id = str(uuid.uuid4())
    
    # Write to outbox
    outbox = {}
    if os.path.exists(outbox_file):
        try:
            with open(outbox_file, 'r') as f:
                outbox = json.load(f)
        except Exception:
            pass
            
    outbox[req_id] = {"question": question, "timestamp": time.time()}
    try:
        with open(outbox_file, 'w') as f:
            json.dump(outbox, f)
    except Exception as e:
        return f"Error: Failed to write to outbox: {e}"
        
    # Poll inbox
    timeout = 300 # Wait up to 5 minutes
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(inbox_file):
            try:
                with open(inbox_file, 'r') as f:
                    inbox = json.load(f)
                if req_id in inbox:
                    status = inbox[req_id]["status"]
                    
                    # Cleanup inbox
                    del inbox[req_id]
                    try:
                        with open(inbox_file, 'w') as f:
                            json.dump(inbox, f)
                    except Exception:
                        pass
                        
                    return status
            except Exception:
                pass
        time.sleep(1)
        
    return "Error: Timeout waiting for Boss's response."

def main():
    mcp.run()

if __name__ == "__main__":
    main()
