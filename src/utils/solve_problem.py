import os
import logging
import re
import tempfile
import pyperclip
from pathlib import Path
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

# Track if we've found Python3
_found_python3 = False

def solve_problem(page: Page, language: str = "Python3") -> bool:
    """
    Get the current problem and solve it using OpenAI
    
    Args:
        page (Page): Playwright page object
        language (str): Programming language to use (default: Python3)
        
    Returns:
        bool: True if successful, False otherwise
    """
    global _found_python3
    
    try:
        # Set window size to ensure consistent layout
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Get current URL
        current_url = page.url
        logging.info(f"Current problem URL: {current_url}")
        
        # Use AgentQL to get problem details
        problem_data = page.query_elements(PROBLEM_QUERY)
        
        # Get current language
        current_lang = problem_data.code_editor.current_language
        current_lang_text = current_lang.text_content()
        logging.info(f"Current language: {current_lang_text}")
        
        # Handle language selection
        if not _found_python3:  # Only try to change language if we haven't found Python3 yet
            if "SQL" in current_lang_text:
                logging.info("SQL problem detected, keeping SQL as language")
            elif current_lang_text == "Python3":
                logging.info("Already using Python3")
                _found_python3 = True
            else:
                try:
                    # Click language selector
                    language_select = problem_data.code_editor.language_select
                    language_select.click()
                    page.wait_for_timeout(1000)
                    
                    # Use a more specific selector for Python3
                    python_option = page.locator("[tf623_id] >> text=Python3").first
                    if python_option.count() > 0:
                        python_option.click()
                        page.wait_for_timeout(1000)
                        # Verify the language was actually changed
                        new_lang = problem_data.code_editor.current_language.text_content()
                        if new_lang == language:
                            logging.info(f"Successfully changed language to {language}")
                            _found_python3 = True
                        else:
                            logging.warning(f"Failed to change language, using {new_lang}")
                    else:
                        logging.info(f"{language} not available, using {current_lang_text}")
                except Exception as e:
                    logging.warning(f"Could not change language: {str(e)}")
        
        # Get problem details
        problem_title = problem_data.problem_title.text_content()
        problem_content = problem_data.problem_content.text_content()
        editor_content = problem_data.code_editor.editor_content.text_content()
        
        # Construct prompt with problem details
        prompt = f"""
        You are a LeetCode problem solver. You will be given the following problem:
        Problem Title: {problem_title}
        Problem Content: {problem_content}
        Problem Link: https://leetcode.com/problems/{problem_title.replace(' ', '-').lower()}
        Current Language: {current_lang_text}
        Editor Content: {editor_content}
        
        Please provide a solution that:
        1. Is efficient and optimized
        2. Includes no comments or any explanation, only the solution
        3. Follows best practices for {current_lang_text}
        4. Uses the code provided in the editor
        5. Make sure it doesn't say '''python3''' in the beginning or end of solution or anything else that indicates you are an AI
        6. IMPORTANT: The solution MUST be wrapped in a Solution class, like this:
           class Solution:
               def method_name(self, params):
                   # your solution here
        """
        
        # Get solution from OpenAI
        logging.info("Getting solution from OpenAI...")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        solution = completion.choices[0].message.content
        
        # Format solution before submitting
        print(f"Current solution: {solution}")
        solution = _format_solution(solution)
        
        # Type the solution into the editor
        editor = problem_data.code_editor.editor_content
        page.locator(".monaco-editor").click()
        page.wait_for_timeout(1000)
        
        # Clear existing content
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        page.wait_for_timeout(1000)
        
        try:
            # Copy solution to clipboard and paste
            pyperclip.copy(solution)
            page.keyboard.press("Control+V")
            page.wait_for_timeout(1000)
        except Exception as e:
            logging.error(f"Error typing solution: {str(e)}")
            return False
        
        # Submit the solution
        page.keyboard.press("Control+A")
        page.wait_for_timeout(100)
        page.keyboard.press("Alt+Shift+F")
        page.wait_for_timeout(2000)
        submit_button = page.locator("text=Submit")
        submit_button.click()
        logging.info("Submitted solution")
        
        # Wait for result
        page.wait_for_timeout(5000)
        
        return True
        
    except Exception as e:
        logging.error(f"Error solving problem: {str(e)}")
        return False

async def _select_language(page: Page) -> str:
    """Select Python3 if available, otherwise use current language."""
    global _found_python3
    
    # Get current language
    current_lang = await _get_current_language(page)
    if current_lang == "Python3":
        _found_python3 = True
        return current_lang
            
    # Skip language selection for SQL problems
    if current_lang == "SQL":
        return current_lang
            
    # Only try changing language if we haven't found Python3 yet
    if not _found_python3:
        try:
            await page.click("[tf623_id='7264']", timeout=5000)  # Language select button
            await page.click("text=Python3", timeout=5000)
            await page.wait_for_timeout(1000)  # Wait for language change to take effect
            new_lang = await _get_current_language(page)
            if new_lang == "Python3":
                _found_python3 = True
                return new_lang
        except Exception as e:
            logging.warning(f"Failed to change language: {str(e)}")
                
    return current_lang

async def _get_current_language(page: Page) -> str:
    problem_data = page.query_elements(PROBLEM_QUERY)
    current_lang = problem_data.code_editor.current_language.text_content()
    return current_lang

def _format_solution(solution: str) -> str:
    """Format the solution for submission."""
    # Remove markdown code block indicators if present
    solution = re.sub(r'^```\w*\n|```$', '', solution.strip())
    
    # Create a temporary file and format it
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(solution)
        tmp_path = tmp.name
    
    try:
        os.system(f"black {tmp_path}")
        with open(tmp_path, 'r') as f:
            formatted = f.read()
        return formatted
    except Exception as e:
        logging.error(f"Error formatting solution: {str(e)}")
        return solution  # Return original if formatting fails
    finally:
        os.unlink(tmp_path)  # Clean up temp file