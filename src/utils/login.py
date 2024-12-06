import os
import time
import logging
import random
from dotenv import load_dotenv
from agentql.ext.playwright.sync_api import Page

# Load environment variables
load_dotenv()
leetcode_username = os.getenv('LEETCODE_USERNAME')
leetcode_password = os.getenv('LEETCODE_PASSWORD')

LOGIN_QUERY = """
{
    username_field
    password_field
    signin_button
}
"""

def random_delay(self):
        """Add random delay between actions to simulate human behavior"""
        delay = random.uniform(1, 5)
        time.sleep(delay)

def login(page: Page) -> bool:
    """Log in to Leetcode account"""
    try:
        page.goto("https://leetcode.com/accounts/login/", wait_until="domcontentloaded")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        
        # Use AgentQL to find login elements
        login_elements = page.query_elements(LOGIN_QUERY)

        # Simulate human behavior to bypass Cloudflare captcha
        logging.info("Attempting to bypass Cloudflare captcha...")
        
        # Add a random delay of 1 to 5 seconds
        time.sleep(random.uniform(1, 5))
        
        # Scroll the page to load additional content
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        
        # Add another random delay of 1 to 5 seconds
        time.sleep(random.uniform(1, 5))
        
        # Attempt to find and click the captcha checkbox
        # try:
        #     captcha_checkbox = page.locator('iframe[src*="api2/anchor"]').frame.locator('#recaptcha-anchor')
        #     captcha_checkbox.click()
        #     logging.info("Captcha checkbox clicked")
        # except Exception as e:
        #     logging.warning(f"Failed to click captcha checkbox: {str(e)}")
        
        # Fill in login details
        login_elements.username_field.type(username, delay=200)
        login_elements.password_field.type(password, delay=200)
        login_elements.signin_button.click()

        # Wait for login to complete by checking for site header
        page.wait_for_selector(".site-header")
        logging.info("Successfully logged in to Leetcode")
        self.random_delay()
        return True
    except Exception as e:
        logging.error(f"Failed to login: {str(e)}")
        return False