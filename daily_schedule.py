import schedule
import time
from helpers_sendgrid import email_per_user

# Schedule the job to run daily at a specific time (e.g., 8:00 AM)
schedule.every().day.at("13:00").do(email_per_user)  # Adjust the time as needed

while True:
    schedule.run_pending()  # Check if a scheduled task is pending
    time.sleep(60)  # Wait one minute before checking again