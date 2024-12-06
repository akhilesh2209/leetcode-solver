import os
import time
import logging
from dotenv import load_dotenv
from agentql.ext.playwright.sync_api import Page

# Load environment variables
load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

LOGIN_QUERY = """
{
    username_field
    password_field
    signin_button
}
"""

def login(page: Page) -> bool:
    """Log in to Leetcode account"""
    try:
        page.goto("https://leetcode.com/accounts/login/")
        
        # Use AgentQL to find login elements
        login_elements = page.query_elements(LOGIN_QUERY)

        # Add wait timer for human verification Captcha
        logging.info("Waiting for user to solve Captcha...")
        time.sleep(10)
        
        # Fill in login details
        login_elements.username_field.type(username, delay=200)
        login_elements.password_field.type(password, delay=200)
        login_elements.signin_button.click()

        # Wait for login to complete by checking for site header
        page.wait_for_selector(".site-header")
        logging.info("Successfully logged in to Leetcode")
        return True
    except Exception as e:
        logging.error(f"Failed to login: {str(e)}")
        return False