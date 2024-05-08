from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tester import *



app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify the domains you want to allow, or use '*' for open access
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def index():
    """
    This is the index page of the API
    """
    return {"message": "Hello World"}

@app.post("/test/")
def execute_test(test: Test):
    """
    This is the function to execute the test
    """
    return test.run_test()



if __name__ == '__main__':
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", default=5000)), log_level="info")

