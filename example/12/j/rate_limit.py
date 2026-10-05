from slowapi import Limiter
from slowapi.util import get_remote_address

# One shared Limiter for the whole app. Requests are counted per client
# IP address, in memory. With several server processes you'd point it at
# Redis instead (Limiter(..., storage_uri="redis://...")) so they share
# one count.
limiter = Limiter(key_func=get_remote_address)
