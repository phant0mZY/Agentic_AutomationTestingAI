
from google import genai
from selenium import webdriver
from selenium.webdriver.common.by import By
import time, json, os
from dotenv import load_dotenv
import docx2txt, PyPDF2


load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
URL = "https://www.amazon.in/ref=nav_logo"
REQ_FILE = "requirements.docx"

def extract_text(file_path):
    """Extract text from .docx or .pdf"""
    if file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    elif file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    else:
        raise ValueError("File must be .docx or .pdf")


def generate_testcases(requirement_text):
    prompt = f"""
    You are a QA automation assistant.
    From the following product requirements, generate 2-3 simple test cases for a website.
    Respond ONLY with a valid JSON array.

    Example:
    [
      {{
        "test_id": "TC001",
        "description": "Check search bar functionality",
        "steps": ["Go to homepage", "Enter a product name", "Click search button"],
        "expected_result": "Search results are displayed"
      }}
    ]

    Requirements:
    {requirement_text}
    """

    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    output = res.candidates[0].content.parts[0].text.strip()

   
    if "```" in output:
        output = output.split("```json")[-1].split("```")[0].strip()

    try:
        return json.loads(output)
    except Exception as e:
        print(" JSON parsing failed:", e)
        print("LLM returned:\n", output)
        return []



def run_testcases(test_cases, url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    for case in test_cases:
        print(f"\n Running {case['test_id']}: {case['description']}")

        for step in case["steps"]:
            html = driver.page_source[:8000]  

            prompt = f"""
            You are a Selenium automation agent.
            Given the following HTML snippet and step instruction "{step}",
            return JSON:
            {{
              "action":"click/input/navigate",
              "locator_type":"id/name/xpath/css",
              "locator_value":"string",
              "value":"optional text for input"
            }}
            HTML:
            {html}
            """

            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            loc_output = res.candidates[0].content.parts[0].text.strip()

            if "```" in loc_output:
                loc_output = loc_output.split("```json")[-1].split("```")[0].strip()

            try:
                loc = json.loads(loc_output)
                element = driver.find_element(getattr(By, loc["locator_type"].upper()), loc["locator_value"])

                if loc["action"] == "input":
                    element.clear()
                    element.send_keys(loc.get("value", ""))
                elif loc["action"] == "click":
                    element.click()

                time.sleep(1)

            except Exception as e:
                print("⚠️ Step failed:", e)
                continue

        print(" Expected:", case["expected_result"])
    driver.quit()



if __name__ == "__main__":
    print(" Extracting requirements...")
    text = extract_text(REQ_FILE)

    print(" Generating test cases...")
    test_cases = generate_testcases(text)
    print(json.dumps(test_cases, indent=2))

    print(" Running test cases on:", URL)
    run_testcases(test_cases, URL)

