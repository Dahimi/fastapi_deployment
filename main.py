from fastapi import FastAPI
from tester import *

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()



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

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", default=5000)), reload=False)

