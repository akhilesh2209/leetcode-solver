import logging
from agentql.ext.playwright.sync_api import Page

RANDOM_QUERY = """
{
    pickone_button
}
"""

def select_random(page: Page) -> bool:
    """Select a random problem"""
    try:
        # Go to the problemset page
        page.goto("https://leetcode.com/problemset/")
        
        # Use AgentQL to find random button
        random_button = page.query_elements(RANDOM_QUERY)
        random_button.pickone_button.click()
        logging.info('Random problem selected')
        return True
    except Exception as e:
        logging.error(f"Failed to select random problem: {str(e)}")
        return False