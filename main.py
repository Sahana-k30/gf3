from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import router
import uvicorn

app = FastAPI()

app.include_router(router, prefix="/api")

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)