import logging
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
logging.basicConfig(level=logging.INFO)


def scroll_down(driver_name: webdriver, script_torun: str, element=None):
    if element:
        driver_name.execute_script(script_torun, element)
        time.sleep(7)
    else:
        driver_name.execute_script(script_torun)
        time.sleep(7)


def fetch_video_details(driver_name: webdriver):
    time.sleep(5)
    try:
        title = driver_name.find_element(By.XPATH, '//*[@id="container"]/h1/yt-formatted-string').get_attribute(
            'innerText')
        try:
            likes = int(
                driver_name.find_element(By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer['
                                                   '1]/a/yt-formatted-string[@id = "text"]').get_attribute(
                    'innerText'))
        except Exception as e:
            likes = 0
        num_comments = 0
        views = 0
        date = driver_name.find_element(By.XPATH, '//*[@id="info-strings"]/yt-formatted-string').get_attribute(
            'innerText')
        channel_name = driver_name.find_element(By.XPATH, '//*[@id="text"]/a').text
        subscribers = driver_name.find_element(By.XPATH, '//*[@id="owner-sub-count"]').text
        subscribers = subscribers.split(' ')[0]
        views = driver_name.find_element(By.XPATH, '//*[@id = "count"]/ytd-video-view-count-renderer/span[1]'). \
            get_attribute('innerText')
        views = (views.split(' ')[0]).replace(',', '')
        comment_section = driver_name.find_element(By.XPATH, '//*[@id="comments"]')
        scroll_down(driver_name, "arguments[0].scrollIntoView();", comment_section)
        time.sleep(1)
        try:
            num_comments = int(driver_name.find_element(By.XPATH, '//ytd-comments/ytd-item-section-renderer/div['
                                                                  '1]/ytd-comments-header-renderer/div['
                                                                  '1]/h2/yt-formatted-string/span[1]').text)
        except:
            num_comments = 0
            print("No comments found for {}".format(title))
    except Exception as e:
        logging.info(e)

    return channel_name, title, views, likes, subscribers, num_comments, date


def fetch_video_comments_details(driver_name: webdriver):
    max_height = driver_name.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver_name.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)

        new_height = driver_name.execute_script("return document.documentElement.scrollHeight")
        if new_height == max_height:
            break
        max_height = new_height
    try:
        if driver_name.find_elements(By.XPATH, '//*[@id="author-text"]'):
            username_list = [un.text for un in driver_name.find_elements(By.XPATH, '//*[@id="author-text"]')]
            comments_list = [c.text for c in driver_name.find_elements(By.XPATH, '//*[@id="content-text"]')]
        else:
            username_list = "no comments yet"
            comments_list = "no comments yet"

    except Exception as e:
        print(f"something went wrong in video comments details: {e}")

    return username_list, comments_list


def generate_all_video_details(vl):
    """Retrieving details of video"""
    logging.info(f"scrapping for {vl}")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.getenv("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    wdriver = webdriver.Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # wdriver = webdriver.Chrome(executable_path=r'chromedriver.exe')

    wdriver.get(vl)
    channel_name, title, views, likes, subscribers, num_comments, date = fetch_video_details(wdriver)
    username_list, comments_list = fetch_video_comments_details(wdriver)
    wdriver.close()

    mydict = {"Channel_name": channel_name, "Video_title": title, "Num Views": views,
              "Num Likes": likes, "Num Subscribers": subscribers,
              "Num Comments": num_comments,
              "video_link": vl, "Publish Date": date, "Commenter's Name": username_list,
              "Comments": comments_list}

    return mydict


def scrape_youtube_data(link: str):

    """Scrapping top 10 video's details of given link"""
    logging.info('Scrapping started')
    video_and_thumbnail_links = []
    all_video_details = []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.getenv("GOOGLE_CHROME_BIN")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # driver = webdriver.Chrome(executable_path=r'chromedriver.exe')

    driver.maximize_window()
    driver.get(link+"/videos")
    logging.info('On Video Tab')
    time.sleep(1)
    scroll_down(driver, "window.scrollTo(0, document.querySelector('#page-manager').scrollHeight);")
    time.sleep(5)

    video_count = len(driver.find_elements(By.XPATH,
                                           '//ytd-item-section-renderer/div[3]/ytd-grid-renderer/div['
                                           '1]/ytd-grid-video-renderer'))
    counter = 1

    # scrapping for 10 videos
    while counter <= 10 and counter <= video_count:
        logging.info('scrapping data')
        base_link = "//ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer" + "[" + \
                    str(counter) + "]"
        video_link = driver.find_element(By.XPATH, base_link + '/div[1]/ytd-thumbnail/a').get_attribute('href')

        if "shorts" not in video_link:
            thumbnail_link = driver.find_element(By.XPATH,
                                                 base_link + '/div[1]/ytd-thumbnail/a/yt-img-shadow/img').get_attribute(
                'src')

            video_and_thumbnail_links.append((video_link, thumbnail_link))
            counter += 1

    logging.info('video and thumbnail links scrapped')

    for vl_th in video_and_thumbnail_links:
        values = (generate_all_video_details(vl_th[0]), vl_th[1])
        all_video_details.append(values)

    driver.close()

    data_json = {
        "data": [d[0] for d in all_video_details],
        "thumbnail": [d[1] for d in all_video_details]
    }

    json_object = json.dumps(data_json, indent=4)
    file_path = "resources/data.json"
    with open(file_path, "w") as outfile:
        outfile.write(json_object)
        logging.info("Data.json saved successfully")


