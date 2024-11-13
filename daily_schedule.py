import subprocess

subprocess.check_call(["pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import schedule
import time
import os

def run_script():
    # Replace with the path to your script
    os.system("python main.py")  # Adjust the path as needed

# Schedule the job to run daily at a specific time (e.g., 8:00 AM)
schedule.every().day.at("06:00").do(run_script)  # Adjust the time as needed

while True:
    schedule.run_pending()  # Check if a scheduled task is pending
    time.sleep(60)  # Wait one minute before checking again