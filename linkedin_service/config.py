import os
from dotenv import load_dotenv
load_dotenv()

# Use an env-var in production, hard-coded value while prototyping
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
MAX_RESULTS = int(os.getenv("LINKEDIN_MAX_RESULTS", 1000))
