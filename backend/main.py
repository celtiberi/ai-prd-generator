import uvicorn
from api.routes import app
from config.settings import Settings

settings = Settings()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 