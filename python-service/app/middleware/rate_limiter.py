from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Rate limit decorators for specific routes:
# - Agent chat: 20/minute (applied via @limiter.limit("20/minute") on the route)
# - Screener: 5/minute (applied via @limiter.limit("5/minute") on the route)
# - Global: 100/minute (default)
