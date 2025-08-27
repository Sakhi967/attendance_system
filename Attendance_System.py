import datetime
import threading
import time
import json
import uuid
import smtplib
from email.mime.text import MIMEText
import qrcode
from PIL import Image
import sys

# Configuration
CLASSROOM_NO = "101"
CLASS_TIME = "10:09"  # Set your class time here (HH:MM) - Update this line
INSTRUCTOR_EMAIL = None  # Set to your email for reminders
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASS = "your_app_password"

# US Federal Holidays for 2025 (add Indian holidays as needed)
HOLIDAYS_2025 = {
    datetime.date(2025, 1, 1), datetime.date(2025, 1, 20), datetime.date(2025, 2, 17),
    datetime.date(2025, 5, 26), datetime.date(2025, 6, 19), datetime.date(2025, 7, 4),
    datetime.date(2025, 9, 1), datetime.date(2025, 10, 13), datetime.date(2025, 11, 11),
    datetime.date(2025, 11, 27), datetime.date(2025, 12, 25),
}

def is_class_day(date):
    if date.weekday() >= 5:
        print(f"Skipping {date}: Weekend")
        sys.stdout.flush()
        return False
    if date in HOLIDAYS_2025:
        print(f"Skipping {date}: Holiday")
        sys.stdout.flush()
        return False
    print(f"{date} is a valid class day")
    sys.stdout.flush()
    return True

def generate_qr_code():
    today = datetime.date.today()
    if not is_class_day(today):
        return None
    data = {"date": str(today), "classroom": CLASSROOM_NO, "unique_id": str(uuid.uuid4())}
    qr_data = json.dumps(data)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    filename = f"qr_attendance_{today}.png"
    img.save(filename)
    print(f"Generated QR code for {today} in {filename}")
    sys.stdout.flush()
    return filename

def send_reminder(message):
    print(message)
    sys.stdout.flush()
    if INSTRUCTOR_EMAIL:
        try:
            msg = MIMEText(message)
            msg['Subject'] = "Class Reminder"
            msg['From'] = SMTP_USER
            msg['To'] = INSTRUCTOR_EMAIL
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)  # Fixed typo
            server.sendmail(SMTP_USER, INSTRUCTOR_EMAIL, msg.as_string())
            server.quit()
            print("Email reminder sent.")
            sys.stdout.flush()
        except Exception as e:
            print(f"Email failed: {e}")
            sys.stdout.flush()

def reminder_thread():
    while True:
        now = datetime.datetime.now()
        class_hour, class_min = map(int, CLASS_TIME.split(':'))
        class_time_today = now.replace(hour=class_hour, minute=class_min, second=0, microsecond=0)
        reminder_time = class_time_today - datetime.timedelta(minutes=5)
        print(f"Checking time: {now.time()} vs Reminder time: {reminder_time.time()}")
        sys.stdout.flush()
        if reminder_time <= now < class_time_today and is_class_day(now.date()):
            send_reminder(f"Reminder: Class in {CLASSROOM_NO} starts in 5 minutes. Show QR code: qr_attendance_{now.date()}.png")
        time.sleep(60)

if __name__ == "__main__":
    print("Starting attendance generator...")
    sys.stdout.flush()
    threading.Thread(target=reminder_thread, daemon=True).start()
    last_date = None
    while True:
        today = datetime.date.today()
        print(f"Checking date: {today}")
        sys.stdout.flush()
        if today != last_date:
            generate_qr_code()
            last_date = today
        time.sleep(3600)