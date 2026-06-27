import os
import tempfile
from drunken_agy.core.utils import load_dotenv

def test_load_dotenv():
    # Setup a temporary .env file
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = os.path.join(tmpdir, '.env')
        with open(env_file, 'w') as f:
            f.write("TEST_ENV_VAR=12345\n")
            f.write("# COMMENT\n")
            f.write("EMPTY=\n")
            
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            load_dotenv()
            assert os.environ.get("TEST_ENV_VAR") == "12345"
        finally:
            os.chdir(old_cwd)
            if "TEST_ENV_VAR" in os.environ:
                del os.environ["TEST_ENV_VAR"]
