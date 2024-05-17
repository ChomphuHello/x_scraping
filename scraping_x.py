import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument("start-maximized")

# Set the path 
# link dowload chromedriver : https://googlechromelabs.github.io/chrome-for-testing/#stable
chrome_driver_path = 'C:/Users/chaya/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe'
service = Service(chrome_driver_path)

# Login to Twitter
def twitter_login(driver, username, password):
    url = 'https://www.twitter.com/login'
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    username_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="username"]')))
    username_field.send_keys(username)
    
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    
    password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[autocomplete="current-password"]')))
    password_field.send_keys(password)
    
    actions.send_keys(Keys.ENTER)
    actions.perform()
    # Wait for login to complete (can be improved with more specific conditions)
    time.sleep(5)

#get id post
def extract_recent_posts(driver, page_url, post_count=2):
    driver.get(page_url)
    time.sleep(5)
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    posts = []
    
    while len(posts) < post_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
        tweet_elements = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        for tweet in tweet_elements:
            if len(posts) >= post_count:
                break
            try:
                href_element = tweet.find_element(By.XPATH, './/a[@role="link"][time]')
                href = href_element.get_attribute('href')
                posts.append(href)
            except Exception as e:
                print("Error extracting tweet data:", e)
                
    return posts

#scape id post
def scrape_twitter_posts(driver, page_url, desired_post_count):
    driver.get(page_url)
    SCROLL_PAUSE_TIME = 2

    try:
        # Scroll to load comments
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find tweet elements
        tweet_elements = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        for tweet in tweet_elements[:desired_post_count]:
            try:
                # Scroll tweet into view
                ActionChains(driver).move_to_element(tweet).perform()
                time.sleep(1)  # Allow some time for scrolling

                username = tweet.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                tweet_text = tweet.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                timestamp = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
                photo_urls = [photo_element.get_attribute("src") for photo_element in tweet.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']/img")]
                href_element = tweet.find_element(By.XPATH, './/a[@role="link"][time]')
                href = href_element.get_attribute('href')

                # Click on the tweet to load comments
                driver.execute_script("arguments[0].click();", href_element)
                time.sleep(2)  # Allow some time for comments to load

                # Find comment elements
                comment_elements =  driver.find_elements(By.XPATH, ".//div[class='css-175oi2r r-1igl3o0 r-qklmqi r-1adg3ll r-1ny4l3l']" and "//article[@data-testid='tweet']" )
                comments = []
                if not comment_elements:
                    comments = None  # Set comments to None if no comments found
                else:
                    for comment in comment_elements:
                        try:
                            comment_username = comment.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text
                            comment_text = comment.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                            comment_timestamp = comment.find_element(By.XPATH, ".//time").get_attribute("datetime")
                            comments.append({
                                "username": comment_username,
                                "text": comment_text,
                                "timestamp": comment_timestamp
                            })
                        except Exception as e:
                            print("Error extracting comment data:", e)

                # Print post details along with comments
                print("===============================================")
                print(f"Username: {username}")
                print(f"Tweet: {tweet_text}")
                print(f"Timestamp: {timestamp}")
                print(f"Photo URLs: {', '.join(photo_urls)}")
                print(f"LINK href URLs: {href}")
                print("************************************************")

                print("Comments:")
                for comment in comments:
                    print(f"Comment Username: {comment['username']}")
                    print(f"Comment: {comment['text']}")
                    print(f"Timestamp: {comment['timestamp']}")
                    print("************************************************")
            except Exception as e:
                print("Error extracting tweet data:", e)
                print("************************************************")
    except Exception as e:
        print("An error occurred:", e)

def main():
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Login to Twitter
        # twitter_login(driver, "username", "password")
        twitter_login(driver, "test_scrapibg", "@password789")
        
        # ไปที่เพจที่ต้องการ อะไรก็ได้
        page_url = "https://x.com/home"
        driver.get(page_url)
        
        # Extract recent posts URLs
        post_count = 2
        page_urls = extract_recent_posts(driver, page_url, post_count)
        
        # Scrape detailed information from the extracted posts
        for url in page_urls:
            scrape_twitter_posts(driver, url, desired_post_count=1)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
