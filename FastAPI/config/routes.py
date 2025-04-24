from routes import api

def setup_routes(app):
    app.include_router(
        api.router,
        tags=["api"],
    )