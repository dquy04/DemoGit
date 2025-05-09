Kenh14 News Scraper
Dự án này là một công cụ cào dữ liệu (web scraper) được xây dựng bằng Python và Selenium để thu thập bài viết từ trang kenh14.vn. Công cụ cào tiêu đề, mô tả, nội dung, URL ảnh và URL bài viết từ các danh mục được chỉ định (Star, Giải trí, Đời sống, Sức khỏe, Học đường) và lưu dữ liệu vào file Excel.
Tính năng

Cào dữ liệu bài viết từ nhiều danh mục trên kenh14.vn.
Thu thập URL ảnh (ví dụ: https://kenh14cdn.com/...png) với liên kết nhấp được trong Excel.
Xử lý lazy-loading và thử lại để đảm bảo cào dữ liệu ổn định.
Lưu dữ liệu vào file Excel với các cột được định dạng rõ ràng.
Ghi log chi tiết để hỗ trợ gỡ lỗi.

Yêu cầu hệ thống

Hệ điều hành: Windows, macOS hoặc Linux.
Python: Phiên bản 3.6 trở lên.
Trình duyệt: Google Chrome (khuyến nghị phiên bản mới nhất).
Kết nối Internet: Cần thiết để truy cập kenh14.vn và tải thư viện.

Hướng dẫn cài đặt
Thực hiện các bước sau để cài đặt và chạy dự án:
1. Tải mã nguồn từ GitHub
Tải dự án về máy tính của bạn:
git clone https://github.com/<tên_người_dùng>/kenh14_news_scraper.git
cd kenh14_news_scraper

Thay <tên_người_dùng> bằng tên người dùng GitHub của bạn.
2. Cài đặt Python
Đảm bảo Python 3.6 trở lên đã được cài đặt. Kiểm tra phiên bản Python:
python --version

Nếu chưa cài, tải và cài đặt Python từ python.org. Đảm bảo thêm Python vào biến PATH của hệ thống trong quá trình cài đặt.
3. Cài đặt thư viện
Dự án sử dụng các thư viện Python được liệt kê trong file requirements.txt. Cài đặt chúng bằng lệnh:
pip install -r requirements.txt

Nội dung file requirements.txt:
selenium==4.18.1
webdriver-manager==4.0.1
pandas==2.2.1
openpyxl==3.1.2
schedule==1.2.1

Nếu gặp lỗi, cập nhật pip:
pip install --upgrade pip

4. Kiểm tra Chrome và ChromeDriver
Công cụ sử dụng Selenium với trình duyệt Chrome. Đảm bảo Google Chrome đã được cài đặt:

Mở Chrome, vào Cài đặt > Giới thiệu về Chrome để kiểm tra phiên bản (ví dụ: 126.0.6478.127).
Thư viện webdriver-manager sẽ tự động tải ChromeDriver tương thích. Nếu gặp lỗi, xóa bộ nhớ cache của webdriver-manager:

# macOS/Linux
rm -rf ~/.wdm

# Windows
del /s /q %USERPROFILE%\.wdm

5. Tạo thư mục lưu dữ liệu
Công cụ lưu file Excel đầu ra vào thư mục data/. Tạo thư mục này nếu chưa có:
mkdir data

Đảm bảo bạn có quyền ghi vào thư mục data/.
Cấu trúc thư mục
BAITAPLON_TDHQT/
├── kenh14.py              # Script chính để cào dữ liệu từ kenh14.vn
├── requirements.txt     # Danh sách các thư viện Python cần thiết
├── data/               # Thư mục lưu file Excel đầu ra (tạo tự động)
└── README.md           # Tài liệu hướng dẫn dự án

Cách sử dụng
1. Chạy công cụ cào dữ liệu
Chạy script để bắt đầu cào dữ liệu:
python main.py


Script sẽ mở một cửa sổ trình duyệt Chrome (chế độ không headless để hỗ trợ gỡ lỗi) và cào dữ liệu từ các danh mục được chỉ định.
Dữ liệu được lưu vào file Excel trong thư mục data/, với tên news_data_YYYYMMDD.xlsx (ví dụ: news_data_20250509.xlsx).

2. Kiểm tra kết quả
Mở file Excel trong thư mục data/ để xem dữ liệu:

Các cột:

Danh mục: Tên danh mục (ví dụ: Star, Giải trí).
Tiêu đề: Tiêu đề bài viết.
Mô tả: Tóm tắt bài viết.
Hình ảnh: URL ảnh (ví dụ: https://kenh14cdn.com/...png). Nhấp để mở ảnh.
Link xem ảnh: Liên kết hiển thị "Xem ảnh" (nhấp để mở ảnh).
Nội dung: Nội dung đầy đủ của bài viết.
URL bài viết: URL của bài viết.


Kiểm tra cột Hình ảnh có chứa URL ảnh hợp lệ và cột Link xem ảnh có liên kết nhấp được.


3. Bật chế độ Headless (Tùy chọn)
Để chạy nhanh hơn mà không mở cửa sổ trình duyệt, bật chế độ headless:

Mở file main.py và bỏ comment dòng sau trong hàm setup_driver:

chrome_options.add_argument("--headless")


Lưu file và chạy lại script:

python main.py

Xử lý lỗi
1. Lỗi "No such file or directory" cho ChromeDriver

Nguyên nhân: webdriver-manager không tải được ChromeDriver.
Cách khắc phục:
Cập nhật webdriver-manager:pip install --upgrade webdriver-manager


Xóa cache:rm -rf ~/.wdm  # macOS/Linux
del /s /q %USERPROFILE%\.wdm  # Windows


Chạy lại script.



2. Không cào được ảnh

Nguyên nhân: Selector không đúng, lazy-loading chưa tải, hoặc bị chặn bởi hệ thống chống bot.
Cách khắc phục:
Kiểm tra log trong terminal, tìm lỗi như Không tìm thấy thẻ <img>.
Kiểm tra HTML thủ công:
Mở kenh14.vn/star.chn trên Chrome.
Nhấp chuột phải vào ảnh, chọn Kiểm tra (Inspect).
Ghi lại selector <img> (ví dụ: <img class="fancybox-image" src="...">).
Cập nhật selector trong main.py:img_elem = article.find_element(By.CSS_SELECTOR, "li.knswli img.<new_class>, ...")




Dùng undetected-chromedriver để chống chặn bot:
Cài đặt:pip install undetected-chromedriver


Sửa hàm setup_driver trong main.py:import undetected_chromedriver as uc
def setup_driver():
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
    chrome_options.add_argument("--blink-settings=imagesEnabled=true")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=chrome_options)
    logging.info("Khởi tạo undetected-chromedriver thành công")
    return driver







3. Timeout hoặc lỗi tải trang

Nguyên nhân: Kết nối mạng chậm hoặc trang kenh14.vn không phản hồi.
Cách khắc phục:
Kiểm tra kết nối Internet.
Tăng thời gian chờ trong main.py:WebDriverWait(driver, 60).until(...)  # Tăng từ 40s lên 60s


Thử lại sau vài phút.



Lưu ý

Chế độ Headless: Chạy ở chế độ không headless để dễ dàng gỡ lỗi. Chỉ bật headless khi đã xác nhận script hoạt động ổn định.
Chống chặn bot: Trang kenh14.vn có thể sử dụng hệ thống chống bot (như Cloudflare). Nếu gặp lỗi liên tục, hãy thử dùng undetected-chromedriver như hướng dẫn ở trên.
Cập nhật Chrome: Đảm bảo Chrome luôn ở phiên bản mới nhất để tránh lỗi tương thích với ChromeDriver.
Tùy chỉnh danh mục: Để thay đổi danh mục cào dữ liệu, chỉnh sửa danh sách categories trong hàm scrape_job của kenh14.py.


