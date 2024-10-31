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
import shutil
from datetime import datetime



def generate_data(holdings):
    value = dict()
 
    historic = pd.DataFrame()
    stocks = list(holdings.keys())

    for stock in stocks:
        info = yf.Ticker(stock)
        value[stock] = holdings[stock] * info.info['regularMarketPreviousClose']
        stock_history = info.history(period="6mo")
        historic = pd.concat([historic, (stock_history['Close'] * holdings[stock]).rename(stock)], axis=1)

    historic['Total'] = historic.sum(axis=1)
    return historic

def generate_plots(holdings):
    value = dict()
    historic = pd.DataFrame()

    stocks = list(holdings.keys())

    if os.path.exists('plots'):
        shutil.rmtree('plots')  # Deletes everything in the directory
        os.makedirs('plots')
    else:
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

    plt.savefig('plots/zzz_portfolio_plot.png')
    plt.close()

    return 'plots/' 


def email_create(sender, to, holdings):
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

    def create_message(sender, to, image_dir):
        """Create an email message with inline images and improved HTML/CSS styling."""
        message = MIMEMultipart('related')
        message['to'] = to
        message['from'] = sender
        message['subject'] = f"Your Daily Porfolio update for {datetime.now().strftime('%B %d, %Y')}"

        # Create HTML content with improved CSS styling
        html_content = f"""
        <html>
        <head>
            <style>
                .email-container {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                h1, h2 {{
                    color: #333;
                }}
                p {{
                    font-size: 1em;
                    color: #333;
                }}
                .image-container img {{
                    display: block;
                    max-width: 100%;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                .footer {{
                    font-size: 0.9em;
                    color: #777;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <h1>Your Daily Portfolio Update Has Landed!</h1>
                <p>{f"Your current portfolio value is ${float(generate_data(holdings)['Total'].iloc[-1]):,.2f}"}</p>
                <div class="image-container">
        """

        # Automatically add all images from the specified directory
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # Add image
                html_content += f'<br><img src="cid:{filename}">'
                # Add caption text (can customize the caption as needed)
                if filename[:4] != "zzz_":
                    caption = f"Current Stock Value: ${float(generate_data(holdings)[filename[:4]].iloc[-1]):,.2f}"  # Customize caption here if needed
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'  # Center-align the caption
                else:
                    caption = f"Portfolio Value"  # Customize caption here if needed
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'  # Center-align the caption


        # Close HTML content
        html_content += """
                </div>
                <div class="footer">
                    <p>Thank you for using my service.</p>
                    <p>Created by AJ Beery | <a href="https://www.linkedin.com/in/aj-beery/">Connect with me!</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Attach the HTML content
        message.attach(MIMEText(html_content, 'html'))

        # Attach images inline
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                with open(os.path.join(image_dir, filename), 'rb') as f:
                    img = MIMEImage(f.read(), name=filename)
                    img.add_header('Content-ID', f'<{filename}>')
                    img.add_header('Content-Disposition', 'inline', filename=filename)
                    message.attach(img)

        # Return the email message in base64 encoded format
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(sender, to, image_dir):
        """Send an email using the Gmail API."""
        # Assuming get_credentials() and service creation are handled here
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Create the email message with inline images
        message = create_message(sender, to, image_dir)
        
        # Send the message
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Email sent successfully: {sent_message['id']}")

    image_directory = generate_plots(holdings)
    # Call `send_email` with the provided arguments
    send_email(sender, to, image_directory)