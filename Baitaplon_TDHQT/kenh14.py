from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import time
import schedule
import os
import logging
import re
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    """Khởi tạo Chrome WebDriver với tùy chọn headless."""
    try:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Tạm tắt headless để debug
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Chống chặn bot
        chrome_options.add_argument("--blink-settings=imagesEnabled=true")  # Bật tải hình ảnh
        chrome_options.add_argument("--window-size=1920,1080")  # Giả lập màn hình lớn
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logging.info("Khởi tạo WebDriver thành công")
        return driver
    except Exception as e:
        logging.error(f"Lỗi khi khởi tạo WebDriver: {e}")
        raise

def scroll_page(driver):
    """Cuộn trang để tải nội dung lazy-load."""
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):  # Cuộn 10 lần
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(6)  # Tăng thời gian chờ
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        # Chờ JavaScript và hình ảnh lazy-load
        WebDriverWait(driver, 25).until(lambda d: d.execute_script("return document.readyState") == "complete")
        try:
            WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.fancybox-image, img.lightbox-content, img[data-src], img[data-lazy-src], img[data-lazyload-src], a.knswli-img"))
            )
        except:
            logging.info("Không tìm thấy hình ảnh lazy-load hoặc link, tiếp tục xử lý")
        logging.info("Đã cuộn trang và chờ JavaScript tải nội dung")
    except Exception as e:
        logging.warning(f"Lỗi khi cuộn trang: {e}")

def scrape_kenh14_category(driver, category_url, category_name, max_pages=2):
    """Cào dữ liệu từ một danh mục trên kenh14.vn."""
    articles_data = []
    page_count = 1

    # Thử tải trang với retry
    for attempt in range(3):
        try:
            driver.get(category_url)
            WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.knswli"))
            )
            scroll_page(driver)  # Cuộn trang
            logging.info(f"Truy cập {category_url} thành công")
            break
        except TimeoutException:
            logging.warning(f"Thử lần {attempt + 1}: Không tải được {category_url}")
            time.sleep(5)
            if attempt == 2:
                logging.error(f"Không thể tải {category_url} sau 3 lần thử")
                return []

    while page_count <= max_pages:
        try:
            # Lấy danh sách bài viết
            articles = WebDriverWait(driver, 40).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.knswli"))
            )
            logging.info(f"[{category_name}] Trang {page_count}: Tìm thấy {len(articles)} bài viết")

            for article in articles:
                try:
                    # Lấy tiêu đề
                    title = ""
                    try:
                        title_elem = article.find_element(By.CSS_SELECTOR, "h3.knswli-title a")
                        title = title_elem.text.strip()
                    except NoSuchElementException:
                        title = "Không tìm thấy tiêu đề"
                        logging.warning(f"[{category_name}] Thiếu tiêu đề cho bài viết")

                    # Lấy mô tả
                    description = ""
                    try:
                        desc_elem = article.find_element(By.CSS_SELECTOR, "div.knswli-sapo, p.knswli-sapo, div.news-sapo, p.sapo, div.sapo")
                        description = desc_elem.text.strip()
                        logging.info(f"[{category_name}] Mô tả bài {title}: {description[:50]}...")
                    except NoSuchElementException:
                        description = "Không có mô tả"
                        logging.info(f"[{category_name}] Không tìm thấy mô tả cho bài: {title}")

                    # Lấy URL bài viết
                    article_url = ""
                    try:
                        article_url = title_elem.get_attribute("href")
                        if not article_url.startswith("http"):
                            article_url = "https://kenh14.vn" + article_url
                    except:
                        article_url = "Không lấy được URL"
                        logging.warning(f"[{category_name}] Thiếu URL cho bài: {title}")

                    # Lấy hình ảnh
                    image_url = ""
                    try:
                        # Thử từ <img> trong danh sách
                        img_elem = article.find_element(By.CSS_SELECTOR, "li.knswli img.fancybox-image, li.knswli img.lightbox-content, a.knswli-img img, a.knswli-thumb img, div.knswli-img img, img.news-img, img.lazy, img.lazyload, img.thumbnail, img[data-thumb], img[data-lazyload], img[data-lazyload-src], img[data-custom], img[data-img]")
                        image_url = (img_elem.get_attribute("src") or
                                     img_elem.get_attribute("data-original") or
                                     img_elem.get_attribute("data-src") or
                                     img_elem.get_attribute("data-lazy-src") or
                                     img_elem.get_attribute("data-lazyload-src") or
                                     img_elem.get_attribute("data-custom") or
                                     img_elem.get_attribute("data-img") or
                                     img_elem.get_attribute("data-lazy") or
                                     img_elem.get_attribute("data-thumb"))
                        logging.info(f"[{category_name}] Thử <img> cho bài {title}: src={img_elem.get_attribute('src')}, data-original={img_elem.get_attribute('data-original')}")
                        if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]) and "placeholder" not in image_url.lower():
                            logging.info(f"[{category_name}] Hình ảnh bài {title} (từ <img>): {image_url}")
                        else:
                            image_url = ""
                    except NoSuchElementException:
                        logging.info(f"[{category_name}] Không tìm thấy thẻ <img> trong danh sách cho bài: {title}")

                    # Nếu không lấy được từ <img>, thử từ <a>
                    if not image_url:
                        try:
                            link_elem = article.find_element(By.CSS_SELECTOR, "a.knswli-img, a.knswli-thumb, a.news-img-link, a.photo-img")
                            image_url = link_elem.get_attribute("href")
                            logging.info(f"[{category_name}] Thử href cho bài {title}: {image_url}")
                            if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                                logging.info(f"[{category_name}] Hình ảnh bài {title} (từ <a href>): {image_url}")
                            else:
                                image_url = ""
                        except NoSuchElementException:
                            logging.info(f"[{category_name}] Không tìm thấy thẻ <a> cho bài: {title}")

                    # Nếu vẫn không có, thử từ CSS background
                    if not image_url:
                        try:
                            bg_elem = article.find_element(By.CSS_SELECTOR, "div.knswli-img[style*='background-image'], a.knswli-img[style*='background-image'], div.knswli-photo[style*='background-image'], div.news-thumb[style*='background-image']")
                            style = bg_elem.get_attribute("style")
                            match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                            if match:
                                image_url = match.group(1)
                                logging.info(f"[{category_name}] Thử background cho bài {title}: {image_url}")
                                if any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                                    logging.info(f"[{category_name}] Hình ảnh bài {title} (từ background): {image_url}")
                                else:
                                    image_url = ""
                            else:
                                image_url = ""
                        except NoSuchElementException:
                            logging.info(f"[{category_name}] Không tìm thấy CSS background cho bài: {title}")

                    # Nếu vẫn không có, thử truy cập trang chi tiết
                    if not image_url and article_url.startswith("http"):
                        try:
                            driver.get(article_url)
                            WebDriverWait(driver, 25).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.knc-content, div.detail-content"))
                            )
                            try:
                                img_elem = driver.find_element(By.CSS_SELECTOR, "div.knc-content img.fancybox-image, div.knc-content img.lightbox-content, div.detail-content img, img.detail-img, img.main-img")
                                image_url = (img_elem.get_attribute("src") or
                                             img_elem.get_attribute("data-original") or
                                             img_elem.get_attribute("data-src") or
                                             img_elem.get_attribute("data-lazyload-src") or
                                             img_elem.get_attribute("data-custom"))
                                logging.info(f"[{category_name}] Thử trang chi tiết cho bài {title}: src={img_elem.get_attribute('src')}, data-original={img_elem.get_attribute('data-original')}")
                                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]) and "placeholder" not in image_url.lower():
                                    logging.info(f"[{category_name}] Hình ảnh bài {title} (từ trang chi tiết): {image_url}")
                                else:
                                    image_url = ""
                            except NoSuchElementException:
                                image_url = ""
                                logging.info(f"[{category_name}] Không tìm thấy ảnh trong trang chi tiết: {article_url}")
                            driver.back()
                            time.sleep(2)
                        except:
                            logging.warning(f"[{category_name}] Lỗi khi truy cập trang chi tiết {article_url}")
                            image_url = ""

                    # Lấy nội dung
                    content = ""
                    if article_url.startswith("http"):
                        for attempt in range(3):
                            try:
                                driver.get(article_url)
                                WebDriverWait(driver, 40).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.knc-content, div.detail-content"))
                                )
                                content_elem = driver.find_element(By.CSS_SELECTOR, "div.knc-content, div.detail-content")
                                content = content_elem.text.strip()
                                logging.info(f"[{category_name}] Đã lấy nội dung từ {article_url}")
                                break
                            except:
                                logging.warning(f"[{category_name}] Thử lần {attempt + 1}: Không lấy được nội dung từ {article_url}")
                                time.sleep(3)
                                if attempt == 2:
                                    content = "Không lấy được nội dung"
                        driver.back()
                        time.sleep(2)

                    # Lưu dữ liệu
                    articles_data.append({
                        "Danh mục": category_name,
                        "Tiêu đề": title,
                        "Mô tả": description,
                        "Hình ảnh": image_url,
                        "Link xem ảnh": f'=HYPERLINK("{image_url}", "Xem ảnh")' if image_url else "",
                        "Nội dung": content,
                        "URL bài viết": article_url
                    })
                    logging.info(f"[{category_name}] Đã cào bài: {title}")
                except Exception as e:
                    logging.warning(f"[{category_name}] Lỗi khi cào bài viết {title}: {e}")
                    continue

            # Chuyển sang trang tiếp theo
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.kbw-next-page")
                if "disabled" in next_button.get_attribute("class"):
                    logging.info(f"[{category_name}] Đã đến trang cuối")
                    break
                next_button.click()
                WebDriverWait(driver, 40).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.knswli"))
                )
                scroll_page(driver)
                page_count += 1
                logging.info(f"[{category_name}] Chuyển sang trang {page_count}")
            except:
                logging.info(f"[{category_name}] Không tìm thấy nút trang tiếp theo hoặc đã hết trang")
                break

        except Exception as e:
            logging.error(f"[{category_name}] Lỗi khi cào trang {page_count}: {e}")
            break

    return articles_data

def save_to_excel(data, filename):
    """Lưu dữ liệu vào file Excel với hyperlink cho hình ảnh."""
    try:
        if not os.path.exists("data"):
            os.makedirs("data")
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False, engine="openpyxl")
        logging.info(f"Đã lưu dữ liệu vào {filename}")
    except Exception as e:
        logging.error(f"Lỗi khi lưu Excel: {e}")

def scrape_job():
    """Công việc cào dữ liệu chính."""
    driver = setup_driver()
    try:
        # Danh sách danh mục
        categories = [
            {"name": "Star", "url": "https://kenh14.vn/star.chn"},
            {"name": "Giải trí", "url": "https://kenh14.vn/musik.chn"},
            {"name": "Đời sống", "url": "https://kenh14.vn/doi-song.chn"},
            {"name": "Sức khỏe", "url": "https://kenh14.vn/suc-khoe.chn"},
            {"name": "Học đường", "url": "https://kenh14.vn/hoc-duong.chn"}
        ]

        all_data = []
        for category in categories:
            logging.info(f"Bắt đầu cào dữ liệu từ {category['name']} ({category['url']})")
            data = scrape_kenh14_category(driver, category['url'], category['name'], max_pages=2)
            all_data.extend(data)
            logging.info(f"Hoàn thành cào {category['name']}: {len(data)} bài viết")

        # Lưu dữ liệu
        if not all_data:
            logging.warning("Không cào được dữ liệu nào từ tất cả danh mục")
        else:
            logging.info(f"Tổng cộng cào được {len(all_data)} bài viết")
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"data/news_data_{date_str}.xlsx"
            save_to_excel(all_data, filename)
        
    finally:
        driver.quit()

def main():
    """Chương trình chính: thiết lập lịch chạy vào 6h sáng hàng ngày."""
    schedule.every().day.at("06:00").do(scrape_job)  # Lên lịch chạy lúc 6h sáng
    logging.info("Đã thiết lập lịch chạy vào 6h sáng hàng ngày")

    while True:
        schedule.run_pending()  # Kiểm tra và chạy các công việc theo lịch
        time.sleep(60)  # Chờ 60 giây trước khi kiểm tra lại

if __name__ == "__main__":
    main()
