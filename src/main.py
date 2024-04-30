from fastapi import FastAPI
import uvicorn
from route.route import router as webauth_r
from test import router as test


app = FastAPI()

app.include_router(webauth_r)
app.include_router(test)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)