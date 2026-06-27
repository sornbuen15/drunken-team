import os
import json
import time
import uuid
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("discord-mcp")

def write_outbox(req_id: str, question: str):
    # Determine the project root to reliably find .agents/
    curr_dir = os.getcwd()
    # If not in project root, assume we can find it by looking for .agents
    agents_dir = os.path.join(curr_dir, '.agents')
    if not os.path.exists(agents_dir):
        # fallback to parent
        agents_dir = os.path.abspath(os.path.join(curr_dir, '..', '.agents'))
    
    outbox_file = os.path.join(agents_dir, 'discord_outbox.json')
    os.makedirs(os.path.dirname(outbox_file), exist_ok=True)
    outbox = {}
    if os.path.exists(outbox_file):
        try:
            with open(outbox_file, 'r') as f:
                outbox = json.load(f)
        except Exception:
            pass
    outbox[req_id] = {"question": question, "timestamp": time.time()}
    with open(outbox_file, 'w') as f:
        json.dump(outbox, f)

def read_inbox(req_id: str):
    curr_dir = os.getcwd()
    agents_dir = os.path.join(curr_dir, '.agents')
    if not os.path.exists(agents_dir):
        agents_dir = os.path.abspath(os.path.join(curr_dir, '..', '.agents'))
        
    inbox_file = os.path.join(agents_dir, 'discord_inbox.json')
    if os.path.exists(inbox_file):
        try:
            with open(inbox_file, 'r') as f:
                inbox = json.load(f)
            if req_id in inbox:
                status = inbox[req_id]["status"]
                del inbox[req_id]
                with open(inbox_file, 'w') as f:
                    json.dump(inbox, f)
                return status
        except Exception:
            pass
    return None

@mcp.tool()
def ask_boss(question: str) -> str:
    """
    Ask the Boss for approval via Discord.
    Blocks execution until the Boss reacts (👍/👎/🌟).
    """
    req_id = str(uuid.uuid4())
    write_outbox(req_id, question)
    
    while True:
        status = read_inbox(req_id)
        if status:
            return status
        time.sleep(1)

@mcp.tool()
def execute_remote_command(command: str, require_approval: bool = True) -> str:
    """
    Execute a terminal command on the host securely.
    If require_approval is True, asks the Boss on Discord first.
    """
    if require_approval:
        approval_text = (
            f"🚨 **APPROVAL REQUIRED (Secure Session)** 🚨\n"
            f"💻 **Machine:** Jakkawan-MacBook Pro (Hash: 🦊 🚀 🔵)\n"
            f"🤖 **AI Session:** c32b91bd-971c-457b-b36f-f0020367390b\n"
            f"📂 **Context:** Testing Zero-Trust Security Workflow\n"
            f"⚠️ **Action:** Execute command `{command}`\n"
            f"⏱️ **Time:** {time.strftime('%I:%M %p')} (Link expires in 5 mins)\n\n"
            f"🔒 **WebAuthn Passkey Verification Required:**\n"
            f"🔗 https://webauthn.io/ (Simulated Auth Link)\n"
            f"*(Note: In the real app, this link will trigger Face ID. For this test, click 👍 after you simulate it!)*"
        )
        status = ask_boss(approval_text)
        if status not in ("approved", "approved_always"):
            return f"Execution rejected by Boss (Status: {status})"
            
    try:
        res = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Exit Code: {res.returncode}\nStdout: {res.stdout}\nStderr: {res.stderr}"
    except Exception as e:
        return f"Error executing command: {e}"

if __name__ == "__main__":
    mcp.run()
