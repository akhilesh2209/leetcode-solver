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

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leetcode_solver.log', encoding='utf-8'),
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
            
            try:
                # Login
                if not login(page):
                    raise Exception("Failed to login")
                
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
            
            finally:
                browser.close()
            
    except Exception as e:
        logging.error(f"Error encountered: {str(e)}")
        raise

if __name__ == '__main__':
    main()