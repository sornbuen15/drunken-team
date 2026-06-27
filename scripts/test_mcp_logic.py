import sys
import os

# Add scripts to path to import discord_mcp_server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from discord_mcp_server import execute_remote_command

def main():
    print("Testing the remote command execution with Discord approval...")
    # This will ask Discord, wait for reaction, and if approved, run the command
    result = execute_remote_command('echo "Hello from the other side! Approval worked!"', require_approval=True)
    print("Final Result from Execution:")
    print(result)

if __name__ == "__main__":
    main()
