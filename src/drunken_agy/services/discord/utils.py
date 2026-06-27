import os
import json
import time
from drunken_agy.core.utils import find_config

def log_activity(event_type, author, content):
    config_file = find_config('discord_config.json')
    project_path = os.path.dirname(os.path.dirname(config_file)) if config_file else os.getcwd()
    activity_file = os.path.join(project_path, ".agents", "discord_activity.jsonl")
    
    event = {
        "timestamp": time.time(),
        "type": event_type,
        "author": author,
        "content": content
    }
    
    try:
        with open(activity_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass

def extract_clean_response(log_content):
    lines = log_content.split('\n')
    cleaned_lines = []
    in_thinking = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track thinking tags
        if stripped == "<thinking>":
            in_thinking = True
            continue
        if stripped == "</thinking>":
            in_thinking = False
            continue
        if in_thinking:
            continue
            
        # Filter out system logs or tool output marker lines
        if (stripped.startswith("I will ") or 
            stripped.startswith("I'm checking ") or 
            stripped.startswith("I'm initializing ") or
            stripped.startswith("I am initializing ") or
            stripped.startswith("Executing command: ") or
            stripped.startswith("Running command: ") or
            stripped.startswith("[System]") or
            stripped.startswith("[Warning]") or
            stripped.startswith("Warning:") or
            stripped.startswith("[Info]")):
            continue
            
        cleaned_lines.append(line)
        
    # Clean up consecutive blank lines
    result_lines = []
    prev_blank = False
    for line in "\n".join(cleaned_lines).strip().split('\n'):
        if not line.strip():
            if not prev_blank:
                result_lines.append(line)
                prev_blank = True
        else:
            result_lines.append(line)
            prev_blank = False
            
    return "\n".join(result_lines).strip()
