from .settings import *

# Override database settings for development with SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

print("🐍 Using SQLite database for development") 