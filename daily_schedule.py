import schedule
import time
from helpers_sendgrid import email_per_user, email_init, email_error

email_init()

# Schedule the job to run daily at a specific time (e.g., 8:00 AM)
schedule.every().day.at("13:00").do(email_per_user)  # Adjust the time as needed

while True:
    try:
        # Run scheduled jobs
        schedule.run_pending()
        time.sleep(60)  # Wait for a minute before checking again
    except Exception as e:
        # Catch all exceptions, send an error email, and continue the loop
        error_message = str(e)
        email_error(error_message)
        print(f"Error encountered: {error_message}. Continuing execution.")