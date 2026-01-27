from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return "1234567890"

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)