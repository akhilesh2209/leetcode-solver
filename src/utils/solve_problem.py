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

def solve_problem(page: Page, language: str = "Python3") -> bool:
    """
    Get the current problem and solve it using OpenAI
    
    Args:
        page (Page): Playwright page object
        language (str): Programming language to use (default: Python3)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current URL
        current_url = page.url
        logging.info(f"Current problem URL: {current_url}")
        
        # Use AgentQL to get problem details
        problem_data = page.query_elements(PROBLEM_QUERY)
        
        # Get current language and only change if Python3 is available
        try:
            current_lang = problem_data.code_editor.current_language
            logging.info(f"Current language: {current_lang.text_content()}")
            
            # Only attempt to change language if it's not what we want
            if current_lang.text_content() != language:
                try:
                    language_select = problem_data.code_editor.language_select
                    language_select.click()
                    page.wait_for_timeout(1000)  # Wait for dropdown
                    
                    # Try to find Python3 in the dropdown
                    python_option = page.locator(f"text={language}")
                    if python_option.count() > 0:
                        python_option.click()
                        logging.info(f"Changed language to {language}")
                    else:
                        logging.info(f"{language} not available, using {current_lang.text_content()}")
                except Exception as e:
                    logging.warning(f"Failed to change language: {str(e)}")
        except Exception as e:
            logging.warning(f"Could not determine current language: {str(e)}")
        
        # Get problem details
        problem_title = problem_data.problem_title.text_content()
        problem_content = problem_data.problem_content.text_content()
        
        # Construct prompt with problem details
        prompt = f"""
        Problem Title: {problem_title}
        Problem Content: {problem_content}
        
        Please provide a solution to this LeetCode problem that:
        1. Is efficient and optimized
        2. Includes clear comments explaining the approach
        3. Handles all edge cases
        4. Follows best practices for the current programming language
        """
        
        # Get solution from OpenAI
        logging.info("Getting solution from OpenAI...")
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        solution = completion.choices[0].message.content
        
        # Type the solution into the editor
        editor = problem_data.code_editor.editor_content
        editor.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.wait_for_timeout(500)
        
        # Type solution in chunks to avoid issues
        chunk_size = 100
        for i in range(0, len(solution), chunk_size):
            chunk = solution[i:i + chunk_size]
            page.keyboard.type(chunk)
            page.wait_for_timeout(100)
        
        return True
        
    except Exception as e:
        logging.error(f"Error solving problem: {str(e)}")
        return False