import os
import sys
# from dotenv import load_dotenv
from google import genai
from google.genai import types

# load_dotenv() # load vars from .env file
# api_key = os.getenv("GEMINI_API_KEY")
# print(f"GEMINI_API_KEY : {api_key[:5]}...")

def generate_queries_json(api_key, assn_path="Lab-Exercises/assn.pdf"):
    # FILE I/O to store responses
    # response_hub_path = "responses"
    response_hub_path = "/"
    os.makedirs(response_hub_path, exist_ok=True)


    # num = 1
    # fname = f"resp{num}"
    # resp_path = os.path.join(response_hub_path, fname)
    # while os.path.exists(resp_path + ".txt"):
    #     num += 1
    #     fname = f"resp{num}"
    #     resp_path = os.path.join(response_hub_path, fname)
        # print(fname)
    f = open("queries.json", "w")

    client = genai.Client(api_key=api_key)
    prompt = """
    You are a SQL extraction and generation engine specializing in OracleDB. 

    Your task is to analyze the attached document, extract the database schema and assignment questions, and generate the corresponding SQL queries in a strict JSON format.

    ### OUTPUT FORMAT
    Return a single, raw JSON object (no Markdown, no code blocks, no introductory text) with this structure:
    {
    "setup_queries": [
        {
        "q": "Description (e.g., Create Startups Table)",
        "sql": "VALID_ORACLE_SQL"
        }
    ],
    "assignments": [
        {
        "q": "The exact question text from the document",
        "sql": "VALID_ORACLE_SQL_SOLUTION"
        }
    ]
    }

    ### STRICT RULES
    1. **Dialect:** Use standard OracleDB syntax (e.g., `VARCHAR2`, `NUMBER`, `SYSDATE`).
    2. **Table Naming:** EVERY table name must be prefixed with 'bce5567_'. 
    - Example: If the doc says 'Startups', you write 'bce5567_Startups'.
    - This applies to `CREATE`, `INSERT`, `SELECT`, `FROM`, `JOIN`, and `REFERENCES` clauses.
    3. **Insert Format:** Group all `INSERT` statements for a single table into one JSON entry. Separate individual `INSERT` commands with a semicolon and a newline character (`\n`).
    4. **Cleanliness:** Do not include SQL comments. Do not use Markdown formatting (i.e., do not start with ```json).
    5. **Completeness:** `setup_queries` must include table creation and data population. `assignments` must answer all questions found in the document. 
    6. **Input Variables:** Do NOT use SQL*Plus substitution variables (like `&variable_name`). If a query requires user input, use a hardcoded dummy value instead of `&` variables to prevent execution errors. If a string is required, ensure it fits within the column size limits.
    """
    
    if not os.path.exists(assn_path):
        sys.exit(f"Assignment PDF not found at {assn_path}")
    
    uploaded_file = client.files.upload(file=assn_path)
    
    print("[Generating queries from gemini...]")
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt, uploaded_file],
        
        # Use below only for thinking models
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.LOW
            )
        )
    )

    print("[Queries retrieved]")
    f.write(response.text)
    # print(response.text)
    
if __name__ == "__main__":
    generate_queries_json()