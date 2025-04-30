from routes import api
from dotenv import load_dotenv
load_dotenv()

def setup_routes(app):
    app.include_router(
        api.router,
        tags=["api"],
    )