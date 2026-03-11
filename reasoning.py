
from google import genai
from selenium import webdriver
from selenium.webdriver.common.by import By
import time, json, os
from dotenv import load_dotenv
import docx2txt, PyPDF2

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(file_path):
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
    From the following requirements, generate 2-3 simple website test cases.
    Each test case must be JSON like this:
    {{
      "test_id": "TC001",
      "description": "...",
      "steps": ["...", "..."],
      "expected_result": "..."
    }}
    Requirements:
    {requirement_text}
    """

    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return json.loads(res.candidates[0].content.parts[0].text)


def run_testcases(test_cases, url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)

    for case in test_cases:
        print(f"\n Running {case['test_id']}: {case['description']}")
        for step in case["steps"]:
            html = driver.page_source[:8000]  

            prompt = f"""
            You are a Selenium testing agent.
            Given this HTML snippet and step "{step}",
            return JSON: {{"action":"input/click/navigate","locator_type":"id/name/xpath/css","locator_value":"string","value":"if any"}}
            HTML:
            {html}
            """
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            loc = json.loads(res.candidates[0].content.parts[0].text)

            try:
                element = driver.find_element(getattr(By, loc["locator_type"].upper()), loc["locator_value"])
                if loc["action"] == "input":
                    element.clear()
                    element.send_keys(loc.get("value", ""))
                elif loc["action"] == "click":
                    element.click()
            except Exception as e:
                print(" Step failed:", e)
            time.sleep(1)

        print(" Expected:", case["expected_result"])
    driver.quit()

# =====  Main Runner =====
if __name__ == "__main__":
    file_path = "requirements.docx"  # your input document
    url = "https://www.amazon.in/ref=nav_logo"

    print(" Extracting requirements...")
    text = extract_text(file_path)

    print(" Generating test cases...")
    test_cases = generate_testcases(text)
    print(json.dumps(test_cases, indent=2))

    print(" Running test cases...")
    run_testcases(test_cases, url)

