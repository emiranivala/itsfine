import os

def get_env_var(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and not value:
        raise ValueError(f"Environment variable {key} is required.")
    return value

BOT_TOKEN = get_env_var("BOT_TOKEN", required=True)
API_ID = int(get_env_var("API_ID", required=True))
API_HASH = get_env_var("API_HASH", required=True)
ADMINS = int(get_env_var("ADMINS", "7354339460"))
DB_URI = get_env_var("DB_URI", required=True)
DB_NAME = get_env_var("DB_NAME", "thankyou")
ERROR_MESSAGE = get_env_var("ERROR_MESSAGE", "False").lower() in ("true", "1")
