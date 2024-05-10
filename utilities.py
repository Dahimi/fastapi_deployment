from typing import Literal, Type, List
import google.generativeai as genai
from pydantic import BaseModel, Field
from mirascope.gemini import GeminiExtractor

genai.configure(api_key="AIzaSyBADIu2eLX_Nr7wOO6UpTSXb0d_Evj5j24")

 

class CodeReview(BaseModel):
    original_code: str = Field(description="The original code to be reviewed. If not provided, the default is 'Not provided'.")
    bugs_and_potential_errors: str = Field(description="The bugs and potential errors in the original code. If none are found, the default is 'No bugs or potential errors found'.")
    refactored_code: str = Field(description="The refactored code. If refactoring is not applicable, the default is 'Refactoring not applicable'.")
    changes: str = Field(description="The changes made to the original code. If no changes were made, the default is 'No changes made'.")
    improvement_ideas: str = Field(description="The improvement ideas for the original code. If none are provided, the default is 'No improvement ideas provided'.")
    warnings: str = Field(description="The warnings for the original code. If no warnings are found, the default is 'No warnings found'.")


class CodeReviewExtractor(GeminiExtractor[CodeReview]):
    extract_schema: Type[CodeReview] = CodeReview
    prompt_template = """
    Extract the the code review details from the given text.
    {review_code}
    """

    review_code: str

class TestResults(BaseModel):
    passed_tests: int = Field(description="The number of passed tests.")
    failed_tests: int = Field(description="The number of failed tests.")
    total_tests: int = Field(description="The total number of tests run.")
    time_taken: float = Field(description="The time taken to run the tests in seconds.")


class TestResultsExtractor(GeminiExtractor[TestResults]):
    extract_schema: Type[TestResults] = TestResults
    prompt_template = """
    For the following test code :
    {test_code}

    Extract the the test results from the given output of running a test program.
    {test_results}
    """

    test_results: str
    test_code : str

