import os
import time

from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

link = 'https://appstoreconnect.apple.com/'

# Chrome driver options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1920x1080")

## run web driver and assign to the driver variable
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
    driver.get(link)
    wait = WebDriverWait(driver, 10)

    ## make sure page redirects to the auth form
    is_login_form_visible = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID,"aid-auth-widget-iFrame")))

    if is_login_form_visible:
        load_dotenv()

        ## find email text form and fill with account
        account_field = wait.until(EC.element_to_be_clickable((By.ID, "account_name_text_field")))
        account_field.send_keys(os.getenv('APPLE_ACCOUNT'))
        time.sleep(2)
        account_field.send_keys(Keys.ENTER)

        ## activate remind me checkbox to avoid next enter login process
        remember_me = wait.until(EC.element_to_be_clickable((By.ID, "remember-me-label")))
        remember_me.click()

        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password_text_field")))
        password_field.send_keys(os.getenv('APPLE_PWD'))
        password_field.send_keys(Keys.ENTER)

        is_security_code_container = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "security-code")))

        if is_security_code_container:
            code = input()

            for n, item in enumerate(code, start=0):
                id = 'char' + str(n)
                code_entry = wait.until(EC.element_to_be_clickable((By.ID, id)))
                code_entry.send_keys(item)

            trust_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="button-bar"]//button[3]')))
            trust_btn.click()

            driver.get('https://appstoreconnect.apple.com/apps/1572271000/appstore/activity/ios/ratingsResponses?m=')

            ##TODO: -Need to fix this code first-
            # reviews_wait = WebDriverWait(driver, 20)

            # reviews_container = reviews_wait.until(EC.visibility_of_element_located((By.ID, 'reviews-container')))
            # if reviews_container:
            #     print(driver.page_source)
            # else:
            #     print('Page content is:')
            #     print(driver.page_source)

    ## timeout just to make sure page loads correct and browser didn't closed at the end of the method immediately
    time.sleep(15)

    ## close driver - memory management
    driver.quit()
