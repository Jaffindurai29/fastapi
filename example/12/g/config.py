import os

from dotenv import load_dotenv

load_dotenv()

# !!! DEV ONLY !!! This key is public (it's in git), so anything it
# encrypts is readable by anyone who has this repo. It exists only so the
# lesson runs with zero setup. Real apps: set FERNET_KEY in .env (or a
# secrets manager) and never commit it.
DEV_FERNET_KEY = "BxL7roHgsuzl6NLf-j9jBB6LfGEdkbzrjzR1-0j24cA="

FERNET_KEY = os.getenv("FERNET_KEY", DEV_FERNET_KEY)
