import os
import time
import logging
import random
from dotenv import load_dotenv
from agentql.ext.playwright.sync_api import Page

# Load environment variables
load_dotenv()
EMAIL = os.getenv('LEETCODE_USERNAME')
PASSWORD = os.getenv('LEETCODE_PASSWORD')

LOGIN_QUERY = """
{
    login_form {
        username_field
        password_field
        signin_button
    }
}
"""

VERIFY_QUERY = """
{
    login_form {
        verify_not_robot_checkbox
    }
}
"""

def random_delay():
        """Add random delay between actions to simulate human behavior"""
        delay = random.uniform(1, 5)
        time.sleep(delay)

def login(page: Page, url, browser) -> bool:
    """Log in to Leetcode account"""
    try:
        logging.info(f"Navigating to {url}")
        page.goto(url, wait_until="domcontentloaded")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        
        # Handle Cloudflare checkbox first
        logging.info("Looking for Cloudflare checkbox...")
        try:
            # Wait for iframe to be available
            iframe_locator = page.frame_locator("iframe[title='Widget containing checkbox for hCaptcha security challenge']")
            checkbox = iframe_locator.locator("#checkbox")
            checkbox.wait_for(timeout=10000)  # Wait up to 10 seconds
            checkbox.click()
            logging.info("Clicked Cloudflare checkbox")
            page.wait_for_timeout(2000)  # Wait for animation
        except Exception as e:
            logging.warning(f"Cloudflare checkbox not found or not clickable: {str(e)}")
        
        # Use AgentQL to find login elements
        logging.info("Finding login elements...")
        login_elements = page.query_elements(LOGIN_QUERY)
        
        # Access fields through login_form node
        login_elements.login_form.username_field.type(EMAIL, delay=220)
        login_elements.login_form.password_field.type(PASSWORD, delay=220)
        page.wait_for_timeout(1000)

        # Click sign in button
        login_elements.login_form.signin_button.click()
        page.wait_for_timeout(2000)
        
        # Save login state
        state_path = os.path.join(os.getcwd(), "leetcode_login.json")
        logging.info(f"Saving login state to {state_path}")
        browser.contexts[0].storage_state(path=state_path)
        
        if not os.path.exists(state_path):
            raise Exception("Failed to save login state file")
            
        return True
    except Exception as e:
        logging.error(f"Failed to login: {str(e)}")
        return False