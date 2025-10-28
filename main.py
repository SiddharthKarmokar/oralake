import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from src.routes.sample_routes import router as oracle_router
from src.routes.datalake_routes import router as datalake_router

app = FastAPI()

app.include_router(datalake_router)
app.include_router(oracle_router)
app.include_router(oracle_router, prefix="/oracle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", tags=["default"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status":"ok"
    }

@app.get("/")
def root():
    return {"message": "FastAPI is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, proxy_headers=True)