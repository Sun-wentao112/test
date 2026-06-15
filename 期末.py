from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from pymongo import MongoClient
import time
import random
import bson


def get_driver():

    options = webdriver.EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化检测
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # 设置 user-agent
    driver = webdriver.Edge(options=options)
    return driver


def scrape_job_list(url, city):

    driver = get_driver()
    driver.get(url)
    data = []
    try:
        # 显式等待职位列表加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.jobinfo'))
        )

        # 获取所有职位元素
        job_elements = driver.find_elements(By.CSS_SELECTOR, 'div.jobinfo')
        print(f"Found {len(job_elements)} job elements on page: {url}")

        # 遍历每个职位元素并提取信息
        for job_element in job_elements:
            try:
                # 打印职位元素的 HTML 内容，用于调试
                print("Job element HTML:")
                print(job_element.get_attribute('innerHTML'))

                # 更新薪水提取方法，确保匹配正确的 XPath 或 CSS 选择器
                try:
                    salary_element = job_element.find_element(By.XPATH, './/p[contains(@class, "jobinfo__salary")]')
                    salary = salary_element.text
                except NoSuchElementException:
                    salary = 'N/A'  # 如果没有薪水信息，设为 'N/A'

                # 提取学历要求
                try:
                    education_element = job_element.find_element(By.XPATH, './/div[contains(@class, "jobinfo__other-info-item") and contains(text(), "本科")]')
                    education = education_element.text
                except NoSuchElementException:
                    education = 'N/A'

                # 提取任职资格
                try:
                    experience_element = job_element.find_element(By.XPATH, './/div[contains(@class, "jobinfo__other-info-item")]')
                    experience = experience_element.text
                except NoSuchElementException:
                    experience = 'N/A'

                # 提取招聘岗位
                try:
                    position_element = job_element.find_element(By.XPATH, './/a[contains(@class, "jobinfo__name")]')
                    position = position_element.text
                except NoSuchElementException:
                    position = 'N/A'

                # 提取地址
                try:
                    address_element = job_element.find_element(By.XPATH, './/div[contains(@class, "jobinfo__other-info-item")]/span')
                    address = address_element.text
                except NoSuchElementException:
                    address = 'N/A'

                # 将职位信息添加到列表中
                data.append({
                    'city': city,
                    'salary': salary,
                    'education': education,
                    'experience': experience,
                    'position': position,
                    'address': address
                })
            except Exception as e:
                print(f"Error while scraping job element: {e}")
                continue
    except Exception as e:
        print(f"Error while scraping job list from {url}: {e}")
    finally:
        driver.quit()
    return data


def scrape_website(page_count):
    """
    爬取指定页数的职位信息。

    参数：
    page_count (int): 要爬取的页数。
    """

    city_code = {'大连': '600', '长春': '613', '沈阳': '599', '南京': '635', '无锡': '636', '宁波': '654'}
    data = []

    for city, code in city_code.items():
        print(f"Scraping jobs for city: {city}")
        for page in range(1, page_count + 1):
            url = f'https://www.zhaopin.com/sou/jl{code}/kwB4JMAS33DPH80PPF/p{page}'
            print(f"Scraping page: {url}")
            job_list = scrape_job_list(url, city)
            if job_list:
                data.extend(job_list)
            # 添加随机延时
            time.sleep(random.randint(2, 5))

    # 在保存数据之前，将 ObjectId 转换为字符串
    data = convert_objectid(data)

    # 将数据保存到 JSON 文件
    with open('job_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # 将数据保存到 MongoDB 数据库
    client = MongoClient('mongodb://localhost:27017/')
    db = client['zhaopin_data']
    collection = db['jobs']
    collection.insert_many(data)


def convert_objectid(data):
    """
    遍历数据中的每个元素，将 ObjectId 转换为字符串
    """
    for item in data:
        for key, value in item.items():
            if isinstance(value, bson.ObjectId):
                item[key] = str(value)
    return data


if __name__ == '__main__':
    scrape_website(7)  # 爬取前7页数据