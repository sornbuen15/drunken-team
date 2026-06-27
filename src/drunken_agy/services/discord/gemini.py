import os
import json
import urllib.request
import sys

def query_gemini_direct(prompt, system_instruction=None):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    contents = [{"parts": [{"text": prompt}]}]
    data = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 400,
            "temperature": 0.7
        }
    }
    
    if system_instruction:
        data["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Direct API call error: {e}", file=sys.stderr)
        return None
