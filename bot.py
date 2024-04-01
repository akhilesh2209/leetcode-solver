from time import *
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver

class LeetcodeBot():
    def get_credentials(self):
        with open("credentials.txt") as f:
            content = f.readlines()
        creds = [line.strip() for line in content if not "#" in line]
        return creds[0], creds[1]

    def login(self, email, password, driver):
        driver.maximize_window()
        driver.fullscreen_window()
        driver.get("https://leetcode.com/accounts/login/")
        
        username = driver.find_element(By.ID, "username")
        username.click()
        username.send_keys(email)
        
        pwd = driver.find_element(By.ID, "password")
        pwd.click()
        pwd.send_keys(password)
        sleep(10) # Give person time to verify that they are a human
        
        log = driver.find_element(By.ID, "login")
        log.click()
        sleep(2)
        
    def select_random(self, driver):
        random_button = driver.find_element(By.CLASS_NAME, 
            "flex h-8 w-8 items-center justify-center rounded-full shadow-md from-fixed-green to-green-s dark:to-dark-green-s bg-gradient-to-b shadow-fixed-green")
        try:
            random_button.click()
            print('Random problem selected')
        except:
            pass

    def get_html(self, driver):
        return BeautifulSoup(driver.page_source, "html.parser")
        # print(driver.page_source)

    def get_problem(self, driver):
        current_url = driver.current_url
        pyperclip.copy(current_url)
        print("Current Problem: ", current_url)
        return current_url

    def get_code():
        code = driver.find_element(By.CLASS_NAME, 'view-lines monaco-mouse-cursor-text')
        return code

    def solve(self, driver, current_url, code, llm_client):

        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert programmer but you never comment your code nor explain it, you just output the answer based on the qestion given to you"},
            {"role": "user", "content": "Solve the following problem {url}, make sure the 'Class: Solution' is before any answer given."}
        ]
        )
        # Insert logic for pasting answer
        ans = completion.choices[0].message

    def submit(self, driver):
        submit_button = driver.find_element(By.CLASS_NAME, 
            "py-1.5 font-medium items-center whitespace-nowrap focus:outline-none inline-flex text-label-r bg-green-s dark:bg-dark-green-s hover:bg-green-3 dark:hover:bg-dark-green-3 h-[32px] select-none px-5 text-[12px] leading-[18px] ml-2 rounded-lg")
        try:
            submit_button.click()
            print('Submission successful')
        except:
            pass

    def next_problem(self, driver):
        try:
            next_button = driver.find_element(By.CLASS_NAME,
            'cursor-pointer justify-center hover:text-lc-icon-primary dark:hover:text-dark-lc-icon-primary flex items-center h-[32px] transition-none hover:bg-fill-quaternary dark:hover:bg-fill-quaternary text-gray-60 dark:text-gray-60 w-[32px]'
            )
            next_button.click()
            print("Moving on to the next problem...")
        except:
            pass

    def closedriver(self, driver):
        driver.quit()