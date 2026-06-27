#!/usr/bin/env python3
import sys
import os

# Ensure src/ is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from drunken_agy.core.utils import load_dotenv
load_dotenv()

from drunken_agy.services.discord.bot import main

if __name__ == "__main__":
    main()
