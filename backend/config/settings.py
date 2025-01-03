class Settings:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        
        # Model settings
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.TEST_MODEL = os.getenv("TEST_MODEL", "gpt-3.5-turbo")  # Cheaper model for testing 