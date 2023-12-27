# settings.py

import os
from dotenv import load_dotenv

# Laad omgevingsvariabelen vanuit het .env-bestand (indien aanwezig)
load_dotenv()

# Instellingen
DATABASE_FOLDER = os.path.join(os.getcwd(), 'databases')  # Of een andere gewenste locatie
os.makedirs(DATABASE_FOLDER, exist_ok=True)
DATABASE_NAME = os.path.join(DATABASE_FOLDER, os.getenv("DATABASE_NAME", "fitness.db"))
