from flask import Flask, request, jsonify
import os
import json
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime
import yfinance as yf
import shutil
import base64
from helpers_sendgrid import email_create  # Assuming the email_create function is in a separate file

app = Flask(__name__)
CORS(app)

# Path to the holdings directory
HOLDINGS_DIR = os.path.join(os.getcwd(), 'holdings')

# Ensure holdings directory exists
os.makedirs(HOLDINGS_DIR, exist_ok=True)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json  # Expecting JSON payload
    email = data.get('email')
    stocks = data.get('stocks')

    if not email or not stocks:
        return jsonify({"error": "Email and stocks are required"}), 400

    # Transform the data into the desired format
    transformed_data = {"EMAIL": email}

    # Add each stock ticker and holdings to the transformed_data
    for ticker, holdings in stocks.items():
        transformed_data[ticker] = holdings

    # Path to the user's data file
    file_path = os.path.join(HOLDINGS_DIR, f"{email.replace('@', '_at_')}.json")
    
    # Check if user file exists to determine if it's a new user
    is_new_user = not os.path.exists(file_path)

    # Save user data in a JSON file named after the email
    with open(file_path, 'w') as file:
        json.dump(transformed_data, file)

    # Send a welcome email if it's a new user
    sender = "stocks@ajbeery.com"  # Change to your sender email
    to = email  # Send the email to the email provided in the request

    if is_new_user:
        # Send a welcome email to the user
        welcome_subject = "Welcome to Your Stock Portfolio!"
        welcome_html_content = f"""
        <html>
        <body>
            <h1>Welcome to Your Stock Portfolio, {email}!</h1>
            <p>We're excited to have you on board. Your stock portfolio is ready to go!</p>
            <p>We’ll send you regular updates about your portfolio performance at 8 am CST daily! Stay tuned!</p>
        </body>
        </html>
        """
        # Send the welcome email
        mail = Mail(
            from_email=Email(sender),
            to_emails=To(to),
            subject=welcome_subject,
            html_content=Content("text/html", welcome_html_content)
        )
        try:
            sg = SendGridAPIClient(os.environ.get('sendgrid_api_key'))
            response = sg.send(mail)
            print(f"Welcome email sent successfully: {response.status_code}")
        except Exception as e:
            print(f"Error sending welcome email: {e}")

        try:
            email_create(sender, to, stocks)
        except Exception as e:
            print(f"Error sending updated email: {e}")
    else:
        # Send the regular portfolio update email to the user
        email_create(sender, to, stocks)  # Use the email_create function to send the email with the plots

    return jsonify({"message": "Data saved successfully and email sent!"})

if __name__ == '__main__':
    app.run(port=5000)
