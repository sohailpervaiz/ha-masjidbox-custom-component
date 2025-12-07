DOMAIN = "masjidbox"

DEFAULT_DAYS = 7

API_URL = (
    "https://api.masjidbox.com/1.0/masjidbox/landing/athany/"
    "{slug}?get=at&days={days}&begin={begin}"
)

PLATFORMS: list[str] = ["sensor"]

CONF_SLUG = "slug"
CONF_APIKEY = "apikey"
CONF_DAYS = "days"

COORDINATOR_KEY = "coordinator"
