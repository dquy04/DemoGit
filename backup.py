import os
import shutil
import time
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load thông tin từ file .env
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Đường dẫn thư mục
DB_FOLDER = Path("databases")
BACKUP_FOLDER = Path("backups")

# Hàm gửi email
def send_email(subject, message):
    try:
        # Kết nối với Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        # Tạo email
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        
        # Gửi email
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Đã gửi email!")
    except:
        print("Lỗi gửi email!")

# Hàm backup database
def do_backup():
    try:
        # Tạo thư mục backup nếu chưa có
        if not BACKUP_FOLDER.exists():
            BACKUP_FOLDER.mkdir()
        
        # Lấy thời gian hiện tại
        now = datetime.now().strftime("%d%m%Y_%H%M%S")
        
        # Duyệt các file trong thư mục databases
        for file in DB_FOLDER.iterdir():
            # Chỉ backup file .sql hoặc .sqlite3
            if file.suffix in [".sql", ".sqlite3"]:
                # Tạo tên file backup
                backup_name = f"{file.stem}_{now}{file.suffix}"
                backup_path = BACKUP_FOLDER / backup_name
                
                # Sao chép file
                shutil.copy(file, backup_path)
                print(f"Đã backup {file.name} thành {backup_name}")
        
        # Gửi email thông báo thành công
        send_email(
            "Backup Thành Công",
            f"Đã backup database xong lúc {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}."
        )
    except:
        # Gửi email thông báo lỗi
        send_email(
            "Backup Lỗi",
            f"Có lỗi khi backup database lúc {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}."
        )
        print("Lỗi khi backup!")

# Hàm kiểm tra thời gian để chạy backup
def check_time():
    while True:
        # Lấy giờ hiện tại
        current_time = datetime.now().strftime("%H:%M")
        
        # Nếu là 00:00 thì chạy backup
        if current_time == "00:00":
            do_backup()
        
        # Chờ 60 giây trước khi kiểm tra lại
        time.sleep(60)

# Chạy chương trình
if __name__ == "__main__":
    print("Bắt đầu chương trình backup...")
    check_time()