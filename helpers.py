import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def generate_plots(holdings):
    value = dict()
    historic = pd.DataFrame()

    stocks = list(holdings.keys())

    if not os.path.exists('plots'):
        os.makedirs('plots')

    for stock in stocks:
        plt.figure(figsize=(10,6))
        info = yf.Ticker(stock)
        value[stock] = holdings[stock] * info.info['regularMarketPreviousClose']
        stock_history = info.history(period="6mo")
        historic = pd.concat([historic, (stock_history['Close'] * holdings[stock]).rename(stock)], axis=1)
        plt.plot(stock_history.index, stock_history['Close'] * holdings[stock], marker='o', linestyle='-')
        plt.title(f'Six Month Value of {stock.upper()} - {holdings[stock]} Shares')
        # plt.show

        plot_filename = f'plots/{stock}_plot.png'
        plt.savefig(plot_filename)
        plt.close()


    historic['Total'] = historic.sum(axis=1)
    plt.figure(figsize=(10,6))
    plt.plot(historic.index, historic['Total'], marker='o', linestyle='-')
    plt.title(f'Six Month Value of Portfolio')  
    # plt.show

    plt.savefig('plots/portfolio_plot.png')
    plt.close()

    return 'plots/' 


def email_create(sender, to, subject, message_text, holdings):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def get_credentials():
        """Authenticate and return Gmail API credentials."""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def create_message(sender, to, subject, message_text, image_dir):
        """Create an email message with inline images from a specified directory."""
        message = MIMEMultipart('related')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        # Create the HTML content with images
        html_content = f"<html><body><p>{message_text}</p>"

        # Automatically add all images from the specified directory
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):  # Include only image files
                html_content += f'<img src="cid:{filename}"><br>'
        
        html_content += "</body></html>"
        message.attach(MIMEText(html_content, 'html'))

        # Attach images
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):  # Include only image files
                with open(os.path.join(image_dir, filename), 'rb') as f:
                    img = MIMEImage(f.read(), name=filename)
                    img.add_header('Content-ID', f'<{filename}>')
                    img.add_header('Content-Disposition', 'inline', filename=filename)
                    message.attach(img)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(sender, to, subject, message_text, image_dir):
        """Send an email using the Gmail API."""
        # Assuming get_credentials() and service creation are handled here
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Create the email message with inline images
        message = create_message(sender, to, subject, message_text, image_dir)
        
        # Send the message
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent successfully: {sent_message['id']}")

    image_directory = generate_plots(holdings)
    # Call `send_email` with the provided arguments
    send_email(sender, to, subject, message_text, image_directory)