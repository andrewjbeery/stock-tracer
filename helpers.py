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

    # for stock in stocks:
    #     plt.figure(figsize=(10,6))
    #     info = yf.Ticker(stock)
    #     value[stock] = holdings[stock] * info.info['regularMarketPreviousClose']
    #     stock_history = info.history(period="6mo")
    #     historic = pd.concat([historic, (stock_history['Close'] * holdings[stock]).rename(stock)], axis=1)
    #     plt.plot(stock_history.index, stock_history['Close'] * holdings[stock], marker='o', linestyle='-')
    #     plt.title(f'Six Month Value of {stock.upper()} - {holdings[stock]} Shares')
    #     # plt.show

    #     plot_filename = f'plots/{stock}_plot.png'
    #     plt.savefig(plot_filename)
    #     plt.close()

    for stock in stocks:
        plt.figure(figsize=(10, 6))
        info = yf.Ticker(stock)
        value[stock] = holdings[stock] * info.info['regularMarketPreviousClose']
        stock_history = info.history(period="6mo")
        
        # Calculate the total value based on holdings
        total_value = stock_history['Close'] * holdings[stock]
        historic = pd.concat([historic, total_value.rename(stock)], axis=1)

        # Plotting the line
        plt.plot(stock_history.index, total_value, marker='.', linestyle='-', color='black')

        # Fill between for positive and negative slopes
        for i in range(1, len(total_value)):
            if total_value.iloc[i] > total_value.iloc[i - 1]:
                # Positive slope
                plt.fill_between(stock_history.index[i-1:i+1], total_value.iloc[i-1:i+1], color='green', alpha=0.5)
            else:
                # Negative slope
                plt.fill_between(stock_history.index[i-1:i+1], total_value.iloc[i-1:i+1], color='red', alpha=0.5)

        plt.title(f'Six Month Value of {stock.upper()} - {holdings[stock]} Shares')
        plt.ylim(historic[stock].min() * 0.975, historic[stock].max() * 1.025)  # Adjust as needed

        
        plot_filename = f'plots/{stock}_plot.png'
        plt.savefig(plot_filename)
        plt.close()



    historic['Total'] = historic.sum(axis=1)
    plt.figure(figsize=(10, 6))

    # Plot the line for the total portfolio value
    plt.plot(historic.index, historic['Total'], marker='.', linestyle='-', color='black')

    # Fill between for positive and negative slopes
    for i in range(1, len(historic['Total'])):
        if historic['Total'].iloc[i] > historic['Total'].iloc[i - 1]:
            # Positive slope
            plt.fill_between(historic.index[i-1:i+1], historic['Total'].iloc[i-1:i+1], color='green', alpha=0.5)
        else:
            # Negative slope
            plt.fill_between(historic.index[i-1:i+1], historic['Total'].iloc[i-1:i+1], color='red', alpha=0.5)

    # Set the title
    plt.title('Six Month Value of Portfolio')  
    plt.ylim(historic['Total'].min() * 0.975, historic['Total'].max() * 1.025)  # Adjust as needed

    # Save the plot
    plt.savefig('plots/zzz_portfolio_plot.png')
    plt.close()

    return 'plots/' 


def email_create(sender, to, holdings):
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    historic =generate_data(holdings)
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
                <p>{f"Your current portfolio value is ${float(historic['Total'].iloc[-1]):,.2f}"}</p>
                <div class="image-container">
        """

        # Automatically add all images from the specified directory
        for filename in os.listdir(image_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # Add image
                html_content += f'<br><img src="cid:{filename}">'
                # Add caption text (can customize the caption as needed)
                if filename[:4] != "zzz_":
                    stockname = filename.split('_')[0]
                    caption = f"Current {yf.Ticker(stockname).info['longName']} Value: ${float(historic[stockname].iloc[-1]):,.2f}"
                    calc = (float(historic[stockname].iloc[-1]) - float(historic[stockname].iloc[-2]))
                    calculation = f"{calc:,.2f} From Yesterday"  # Customize caption here if needed
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'
                    if calc > 0:
                        color = "green"
                    else:
                        color = "red"
                    html_content += f'<p style="text-align: center; margin-top: 0; color: {color};">{calculation}</p>'  # Center-align the caption
                else:
                    caption = f"Portfolio Value"  # Customize caption here if needed
                    calc_total = (float(historic['Total'].iloc[-1]) - float(historic['Total'].iloc[-2]))
                    calculation = f"{calc_total:,.2f} From Yesterday"
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'
                    if calc_total > 0:
                        color = "green"
                    else:
                        color = "red"
                    html_content += f'<p style="text-align: center; margin-top: 0; color: {color};">{calculation}</p>'  # Center-align the caption


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