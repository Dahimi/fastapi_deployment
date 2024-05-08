from pydantic import BaseModel, Field
import logging
# from langchain_groq import ChatGroq


# api_key = "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"
# chat = ChatGroq(temperature=0, groq_api_key=api_key, model_name="mixtral-8x7b-32768")

logging.info("here we go again")
class Test(BaseModel):
    code: str
    #make it a field with the options (python, java and javascript)
    language: str = Field(..., description="The language of the code", example="python")
    test_type: str = Field(..., description="The type of test", example="unit")

    def run_test(self):
        print(self)
        return {"code": self.code, "language": self.language, "test_type": self.test_type}


