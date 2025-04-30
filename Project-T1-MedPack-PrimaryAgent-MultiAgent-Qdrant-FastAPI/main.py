import uvicorn
from app.Kernel import app
from config.routes import setup_routes
from dotenv import load_dotenv

load_dotenv()

setup_routes(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=6321
    )
