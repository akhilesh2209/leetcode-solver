import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from agentql.ext.playwright.sync_api import Page

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

PROBLEM_QUERY = """
{
    problem_title
    problem_content
    code_editor {
        language_select
        current_language
        editor_content
    }
}
"""

def solve_problem(page: Page, language: str = "python") -> bool:
    """
    Get the current problem and solve it using OpenAI
    
    Args:
        page (Page): Playwright page object
        language (str): Programming language to use (default: python)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current URL
        current_url = page.url
        logging.info(f"Current problem URL: {current_url}")
        
        # Use AgentQL to get problem details
        problem_data = page.query_elements(PROBLEM_QUERY)
        
        # Select desired programming language
        language_select = problem_data.code_editor.language_select
        if language_select.text_content() != language:
            language_select.click()
            page.get_by_text(language, exact=True).click()
        
        # Construct prompt with problem details
        prompt = f"""
        Problem Title: {problem_data.problem_title.text_content()}
        Problem Content: {problem_data.problem_content.text_content()}
        Programming Language: {language}
        Initial Code:
        {problem_data.code_editor.editor_content.text_content()}
        
        Please provide a complete solution in {language}. Include only 
        the code, no explanations and no comments.
        """
        
        # Get solution from OpenAI
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert programmer. Provide only the code solution, no explanations or comments."},
                {"role": "user", "content": prompt}
            ]
        )
        
        solution = completion.choices[0].message.content
        
        # Clear existing code and input solution
        editor = problem_data.code_editor.editor_content
        editor.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        editor.type(solution)
        page.keyboard.press("Control+Enter")
        
        logging.info("Solution successfully entered")
        return True
        
    except Exception as e:
        logging.error(f"Error solving problem: {str(e)}")
        return False