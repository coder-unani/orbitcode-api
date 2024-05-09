import uvicorn
from fastapi import FastAPI
# from routes import index, auth, external

def create_app():

    # FastAPI initialize
    app = FastAPI()

    # Middleware 정의

    # Router 정의
    # app.include_router(index.router)
    # app.include_router(auth.router, tags=["Authentication"], prefix="/auth")
    # app.include_router(external.router, prefix="/external")
    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app

app = create_app()

# for test
# if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)