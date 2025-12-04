from fastapi import FastAPI
from Backend.Routers.api import router

app = FastAPI(title="Garden Of Eaten API", version="1.0.0")

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
