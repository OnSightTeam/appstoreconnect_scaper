import os
import pickle
import time
import pandas as pd

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
chrome_options.add_argument("user-data-dir=appstoreconnect")

## run web driver and assign to the driver variable
with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) as driver:
    driver.get(link)
    wait = WebDriverWait(driver, 10)

    try:
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
    except:
        print('For website: ', link, 'no cookies')

    ## make sure page redirects to the auth form
    try:
        is_login_form_visible = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID,"aid-auth-widget-iFrame")))

        load_dotenv()

        ## find email text form and fill with account
        account_field = wait.until(EC.element_to_be_clickable((By.ID, "account_name_text_field")))
        if not account_field.get_attribute('value'):
            account_field.send_keys(os.getenv('APPLE_ACCOUNT'))
            account_field.send_keys(Keys.ENTER)

        ## activate remind me checkbox to avoid next enter login process
        #TODO:add check if it's clicked
        remember_me = wait.until(EC.element_to_be_clickable((By.ID, "remember-me-label")))
        remember_me.click()

        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password_text_field")))
        if not password_field.get_attribute('value'):
            password_field.send_keys(os.getenv('APPLE_PWD'))
            password_field.send_keys(Keys.ENTER)

        is_security_code_container = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "security-code")))

        if is_security_code_container:
            code = input()
            for n, item in enumerate(code, start=0):
                id = 'char' + str(n)
                code_entry = wait.until(EC.element_to_be_clickable((By.ID, id)))
                code_entry.send_keys(item)
            time.sleep(10)
            trust_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class="button-bar"]//button[3]')))
            trust_btn.click()

            try:
                cookies = driver.get_cookies()
                pickle.dump(cookies, open("cookies.pkl","wb"))
            except:
                print('Error with load and storing cookies')
    except:
        print("User already logged in")

    driver.get('https://appstoreconnect.apple.com/apps/1572271000/appstore/activity/ios/ratingsResponses?m=')

    time.sleep(15)

    is_page_content_container = wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='legacy']")))
    if is_page_content_container:
        time.sleep(5)

        choose_region = wait.until(EC.element_to_be_clickable((By.ID, "store-fronts-selector-menu")))
        choose_region.click()

        all_regions_option = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "All Countries or Regions")))
        all_regions_option.click()
        time.sleep(2)

        #scroll to bottom of reviews
        reviews_container = wait.until(EC.visibility_of_element_located((By.ID, 'reviews-container')))
        driver.execute_script("arguments[0].scrollIntoView(true);", reviews_container)

        keys = ["title", "author", "review_message"]
        df = pd.DataFrame(columns=keys)

        try:
            reviews = driver.find_elements(By.CLASS_NAME, "review-container")
            # iterate through list and get text
            for review in reviews[:-1]:
                review_data = review.text.split("\n")
                review_data.pop(1)
                review_data.pop(3)
                a_series = pd.Series(review_data, index = df.columns)
                df = df.append(a_series, ignore_index=True)
            print(df)
        except Exception as e:
            print(e)
            print(type(e))

        #timeout just to make sure page loads correct and browser didn't closed at the end of the method immediately
        time.sleep(10)
        driver.quit()