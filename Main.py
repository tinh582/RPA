from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import schedule

import random
from selenium.webdriver.common.by import By


def crawl_dantri():
    print("Bắt đầu lấy dữ liệu từ trang Dân Trí...")

    # Cấu hình trình duyệt không hiển thị + chống lỗi WebGL 
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-unsafe-swiftshader")
    driver = webdriver.Chrome(options=options)

    url = "https://dantri.com.vn" 
    driver.get(url)

    # Kiểm tra và chọn mục tin tức bất kì
    categories = driver.find_elements(By.CSS_SELECTOR, "li.has-child > a")
    if categories:
        print("Các mục tin tức tìm thấy:")
        for category in categories:
            print(f" - {category.text} (Link: {category.get_attribute('href')})")
        category_links = [category.get_attribute("href") for category in categories]
        if category_links:
            # Chọn ngẫu nhiên một mục tin tức
            random_category = random.choice(category_links)
            print(f"Đang mở mục tin tức: {random_category}")
            driver.get(random_category)
        else:
            print("Không có liên kết mục tin tức.")
    articles = []

    while True:
        try:
            print(f"Đang xử lý trang: {driver.current_url}")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article h3 a"))
            )

            links = driver.find_elements(By.CSS_SELECTOR, "article h3 a")

            for link in links:
                try:
                    href = link.get_attribute("href")

                    driver.execute_script("window.open(arguments[0]);", href)
                    driver.switch_to.window(driver.window_handles[1])

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                    )

                    # tiêu đề
                    full_title = driver.find_element(By.CSS_SELECTOR, "h1").text
                    # mô tả
                    try:
                        description = driver.find_element(By.CSS_SELECTOR, "h2.singular-sapo").text
                    except:
                        description = ""
                    # nội dung
                    try:
                        content_element = driver.find_element(By.CSS_SELECTOR, ".singular-content")
                        paragraphs = content_element.find_elements(By.TAG_NAME, "p")
                        content = "\n".join([p.text for p in paragraphs if p.text.strip()])
                    except:
                        content = ""
                    # hình ảnh
                    try:
                        image_element = driver.find_element(By.CSS_SELECTOR, ".singular-content figure img")
                        image_url = image_element.get_attribute("src")
                    except:
                        image_url = ""

                    articles.append({
                        "Tiêu đề": full_title,
                        "Mô tả": description,
                        "Nội dung": content,
                        "Hình ảnh": image_url,
                        "URL": href
                    })

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    print(f"Lỗi khi xử lý bài viết: {e}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # Kiểm tra nút chuyển trang
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.pagination__next")
                next_link = next_button.get_attribute("href")
                if next_link:
                    driver.get(next_link)
                    time.sleep(2)
                else:
                    break
            except:
                break

        except Exception as e:
            print(f"Lỗi khi tải trang: {e}")
            break

    driver.quit()

    if articles:
        df = pd.DataFrame(articles)
        df.to_excel("dantri_data.xlsx", index=False)
        print("Đã lưu toàn bộ dữ liệu vào file Excel.")
    else:
        print("Không có bài viết nào được thu thập.")

crawl_dantri()

schedule.every().day.at("06:00").do(crawl_dantri)
while True:
    schedule.run_pending()
    time.sleep(60)
