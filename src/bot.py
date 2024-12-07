import os
import time
import logging
import agentql
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from agentql.ext.playwright.sync_api import Page

from utils.login import login
from utils.select_random import select_random
from utils.solve_problem import solve_problem

load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv('AGENTQL_API_KEY')
INITIAL_URL = "https://leetcode.com/accounts/login/"

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/leetcode_solver.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    """Main execution function"""
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            page = agentql.wrap(browser.new_page())
            time_start = time.time()
            
            state_path = os.path.join(os.getcwd(), "leetcode_login.json")
            
            # Login
            if not os.path.exists(state_path):
                logging.info("No login state found. Logging in...")
                if not login(page, INITIAL_URL, browser):
                    raise Exception("Failed to login")
                logging.info("Successfully logged in to Leetcode")
            
            try:
                # Create new context with saved login state
                context = browser.new_context(storage_state=state_path)
                page = agentql.wrap(context.new_page())
                page.goto("https://leetcode.com")
                page.wait_for_load_state("networkidle")
                
                # Select random problem
                if not select_random(page):
                    raise Exception("Failed to select random problem")
                
                # Solve problem
                if solve_problem(page):
                    logging.info("Problem solved successfully!")
                else:
                    logging.error("Failed to solve problem")
                
                time_elapsed = time.time() - time_start
                logging.info(f"Total time elapsed: {time_elapsed:.2f} seconds")
                
            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                if os.path.exists(state_path):
                    logging.info("Removing invalid login state file")
                    os.remove(state_path)
                raise e
            
    except Exception as e:
        logging.error(f"Error encountered: {str(e)}")
        raise e

if __name__ == '__main__':
    main()