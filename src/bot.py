import os
import sys
import time
import logging
import random
import agentql
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from agentql.ext.playwright.sync_api import Page

from utils.login import login
from utils.select_random import select_random_problem
from utils.solve_problem import solve_problem

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

load_dotenv()

INITIAL_URL = "https://leetcode.com/accounts/login/"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/leetcode_solver.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    # Get number of problems to solve from command line argument or random
    if len(sys.argv) > 1:
        try:
            num_problems = int(sys.argv[1])
            if num_problems < 1:
                logging.error("Number of problems must be positive")
                return
        except ValueError:
            logging.error("Invalid number of problems specified")
            return
    else:
        num_problems = random.randint(1, 11)  # Random number between 1 and 11
    
    logging.info(f"Starting LeetCode Solver Bot - Will solve {num_problems} problems")
    start_time = time.time()

    with sync_playwright() as p:
        # Launch browser in headless mode for CI/CD
        browser = p.chromium.launch(headless=False)
        state_path = os.path.join(os.getcwd(), "leetcode_login.json")
        
        # Login
        if not os.path.exists(state_path):
            logging.info("No login state found. Logging in...")
            page = agentql.wrap(browser.new_page())
            page.set_viewport_size({"width": 1920, "height": 1080})
            if not login(page, INITIAL_URL, browser):
                logging.error("Failed to login")
                return
            logging.info("Successfully logged in to Leetcode")
        
        try:
            # Create new context with saved login state
            context = browser.new_context(storage_state=state_path)
            page = agentql.wrap(context.new_page())
            page.goto("https://leetcode.com")
            page.wait_for_load_state("networkidle")
            
            # Solve specified number of problems
            problems_solved = 0
            while problems_solved < num_problems:
                logging.info(f"Solving problem {problems_solved + 1}/{num_problems}")
                
                # Select and solve a random problem
                if select_random_problem(page):
                    if solve_problem(page):
                        problems_solved += 1
                        logging.info(f"Successfully solved problem {problems_solved}/{num_problems}")
                    else:
                        logging.error("Failed to solve problem")
                else:
                    logging.error("Failed to select random problem")
                
                # Add a small delay between problems
                time.sleep(2)

            logging.info(f"Successfully solved {problems_solved} problems")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        finally:
            context.close()
            browser.close()

    elapsed_time = time.time() - start_time
    logging.info(f"Total time elapsed: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
