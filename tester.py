from pydantic import BaseModel, Field
import logging
from langchain_groq import ChatGroq
import re
import json
from utilities import CodeReview, CodeReviewExtractor, TestResults, TestResultsExtractor
from prompts import *
api_key = "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"
llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama3-70b-8192")

class Test(BaseModel):
    code: str
    language: str = Field(..., description="The language of the code", example="python")
    test_type: str = Field(..., description="The type of test", example="unit")

    def run_test(self):
        print("Running test")

        with open("input.py", "w") as f:
            f.write(self.code)
        
        # generate test code
        logging.info("Generating test code")
        generated_test = self.generate_test()
        
        # review the code
        logging.info("Reviewing code")
        code_review = self.review_code()
        
        
        # executing the test code
        logging.info("Executing test code")
        test_results = self.execute_test()

        # exract the test results
        logging.info("Extracting test results")
        test_results_stats = self.extract_test_results_stats(test_results, generated_test)
        test_results_reformatted = self.reformat_test_results(test_results, generated_test)
        results = {"generated_test_code": generated_test, "reviewed_code": code_review, "test_results": test_results_reformatted, "test_results_stats": test_results_stats}
        with open("results.json", "w") as f:
            for key, value in results.items():
                f.write(f"{key} : {value}\n\n")
        return results


    def generate_test(self, tries=0):
        use_pytest = "Use the pytest library" if ( self.test_type=="unit" and self.language=="python") else ""
        prompt = f"""You are a professional QA tester. Your goal is to write {self.test_type} tests for the following code. 
        {use_pytest}
        In the test code Remember to include all the dependencies (class defintions, methods, ...) that are used in the test so that I can run the code successufully.
        The provided code is available in input.py file. So import the code from input.py file and write the test code.
        Here is the code :
        ### START ###
        {self.code}
        ### END ###
        Make sure the tests use the language's testing tools (e.g. pytest for Python, JUnit for Java, etc.)
        Use triplet code to delimit your code and start with ### START ### and end with ### END ### like in the example below.
        '''
        ### START ###
        def test_add():
            assert add(1, 2) == 3
            assert add(0, 0) == 0
            assert add(-1, 1) == 0
        ### END ###
        '''
        Don't forget to include and import all the necessary dependencies. Provide Valid code
        I only want the test code and there no need to run the tests.
        """
        code = llm.predict(prompt)
        try :
            # get test code from the json
            extract_code_btw_triplets = re.compile(r'### START ###(.*?)### END ###', re.DOTALL)
            test_code = extract_code_btw_triplets.findall(code)[0]
            with open("output.py", "w") as f:
                f.write(test_code)
            return test_code
        except Exception as e:
            if tries > 3:
                with open("output.py", "w") as f:
                    f.write(code)
                return code
            logging.error(f"Failed to generate test, trying again, error is : {e}")
            return self.generate_test(tries+1)



    def review_code(self):
        prompt = f"""You are a professional developer. 
        Your goal is to refactor and document the following code which is in {self.language} so that it follows coding best practices (comments, docstrings, etc) of this programming language.
        Here is the code :
        ### START ###
        {self.code}
        ### END ###

        Don't forget to insert the $ delimiter at the beginning and end of your code.
        Also, before providing the reviewed code, highlight any bugs or potential errors in it. Feel free to also provide some warnings or improvment ideas to the user!
        Your Output should be in the structure of this example {review_code}

        """
        reviewed_code = llm.predict(prompt)
        # take the part from test_results starting from **Code Review** (included) to the end
        reviewed_code = reviewed_code[reviewed_code.index("**Code Review**"):]
        return reviewed_code


    def execute_test(self):
        if self.test_type == "unit" and self.language == "python":
            print("Executing test code")
            # execute the test code in the output.py file: use subprocess
            import subprocess
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    output = subprocess.check_output(["pytest", "output.py"], text=True)
                    logging.info(f"Output of running test code: {output}")
                    return output
                except Exception as e:
                    logging.error(e)
                    logging.error(f"Failed to execute test, attempt {attempt+1} of {max_attempts}")
                    self.generate_test()
            return "Failed to execute test"

    def extract_test_results_stats(self, test_results, test_code):
        try:
            test_results = TestResultsExtractor(test_results=test_results, test_code=test_code).extract()
            assert isinstance(test_results, TestResults)
            logging.info(f"Test results after extraction: {test_results.model_dump_json()}")
            return test_results.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error("Failed to extract test results, trying again")
            return test_results

    def reformat_test_results(self, test_results, test_code):
        # The results of the tests. Each result is a dictionary with keys 'test_name', 'status', and 'error'. 'error' is only present if 'status' is 'failed'."
        try:
            prompt = f""""
            
            For the following test code :
            {test_code}
            
            Extract the the test results from the given output of running a test program.
            {test_results}

            The results of the tests contains subsection. Each subsection is result and contains 'test_name', 'status', and 'error'. 'error' is only present if 'status' is 'failed'.
            Exemple of the test results is :
            {test_results_example}

            GIVE YOUR ANSWER DIRECTLY IN THE FORMAT OF THE EXAMPLE ABOVE
            
            """
            test_results = llm.predict(prompt)
            test_results = test_results[test_results.index("#"):]
            return test_results
        except Exception as e:
            logging.error(e)
            logging.error("Failed to reformat test results")
            return test_results