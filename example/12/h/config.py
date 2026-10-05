import os

from dotenv import load_dotenv

load_dotenv()

# a-z, A-Z, 0-9 in a shuffled order. Change it (once, before launch) so
# your ids differ from everyone else running this code.
SQIDS_ALPHABET = os.getenv(
    "SQIDS_ALPHABET", "DpNyH4T2PcXBCbfRnV8s6qg7kwrhAOGLKQ0Uaot1ix9zvSjZMEuldWeFIYJm35"
)
# Pad short ids so id 1 isn't a tell-tale 1-2 character string.
SQIDS_MIN_LENGTH = 8
