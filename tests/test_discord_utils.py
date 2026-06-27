from drunken_agy.services.discord.utils import extract_clean_response

def test_extract_clean_response():
    raw_log = """
[System] Starting up
I will execute the command now.
<thinking>
This is an internal thought that should be hidden.
</thinking>
Executing command: ls
Here is the result!
"""
    clean = extract_clean_response(raw_log)
    assert "Here is the result!" in clean
    assert "<thinking>" not in clean
    assert "This is an internal thought" not in clean
    assert "I will execute" not in clean
    assert "[System]" not in clean
