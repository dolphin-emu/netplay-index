"""Global Settings"""

## API

# How long until timed-out sessions are cleaned up
SESSION_CLEANUP_DELAY = 30

# How long until sessions time out
SESSION_TIMEOUT_SECONDS = 15

# Valid regions for sessions
VALID_REGIONS = ["AF", "CN", "EA", "EU", "NA", "OC", "SA"]

# The maximum size transmitted string fields are allowed to have
SESSION_MAX_STRING_LENGTH = 64

# The maximum amount of sessions a single host can have simultaneously
MAXIMUM_SESSIONS_PER_HOST = 5

GEOIP_DATABASE_PATH = "GeoLite2-Country.mmdb"

## Login

# How long every single login attempt should take in seconds
LOGIN_ATTEMPT_DELAY = 1
