import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from datetime import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import json


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
    historic = generate_data(holdings)

    def create_message(sender, to, image_dir):
        """Create an email message with inline images and improved HTML/CSS styling."""
        value = (str(historic['Total'].iloc[-1]))
        # Start HTML content with improved CSS styling
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
                <h1>Your Daily Portfolio Update Has Landed!<br /></h1>
                <time>{datetime.now().strftime('%B %d, %Y')}</time>
                <p>‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ 
                  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎   </p>
                <p>{f"Your current portfolio value is ${float(historic['Total'].iloc[-1]):,.2f}"}</p>
                <div class="image-container">
        """

        attachments = []
        
        # Process images and add Content-ID references in HTML
        for idx, filename in enumerate(sorted(os.listdir(image_dir))):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                cid = f"image{idx}"
                html_content += f'<br><img src="cid:{cid}">'
                
                # Captions for each image
                if filename[:4] != "zzz_":
                    stockname = filename.split('_')[0]
                    caption = f"Current {yf.Ticker(stockname).info['longName']} Value: ${float(historic[stockname].iloc[-1]):,.2f}"
                    calc = (float(historic[stockname].iloc[-1]) - float(historic[stockname].iloc[-2]))
                    calculation = f"{calc:,.2f} From Yesterday"
                    color = "green" if calc > 0 else "red"
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'
                    html_content += f'<p style="text-align: center; margin-top: 0; color: {color};">{calculation}</p>'
                    html_content += f'<p style="text-align: center; margin-top: 0;">Stock Value:${yf.Ticker(stockname).info["regularMarketPreviousClose"]}</p>'
                else:
                    caption = "Portfolio Value"
                    calc_total = (float(historic['Total'].iloc[-1]) - float(historic['Total'].iloc[-2]))
                    calculation = f"{calc_total:,.2f} From Yesterday"
                    color = "green" if calc_total > 0 else "red"
                    html_content += f'<p style="text-align: center; margin-top: 0;">{caption}</p>'
                    html_content += f'<p style="text-align: center; margin-top: 0; color: {color};">{calculation}</p>'

                # Read and attach image with Content-ID
                with open(os.path.join(image_dir, filename), 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    attachment = Attachment(
                        file_content=img_data,
                        file_type="image/png",  # Set MIME type as a string
                        file_name=filename,
                        disposition="inline",  # Use "inline" as a string
                        content_id=cid
                    )
                    attachments.append(attachment)

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

        # Create the SendGrid Mail object
        mail = Mail(
            from_email=Email(sender),
            to_emails=To(to),
            subject=f"Your Daily Portfolio Update for {datetime.now().strftime('%B %d, %Y')}",
            html_content=Content("text/html", html_content)
        )

        # Attach inline images to the email
        for attachment in attachments:
            mail.add_attachment(attachment)

        return mail

    def send_email(sender, to, image_dir):
        """Send an email using SendGrid."""
        try:
            sg = SendGridAPIClient(os.environ.get('sendgrid_api_key'))
            mail = create_message(sender, to, image_dir)
            response = sg.send(mail)
            print(f"Email sent successfully: {response.status_code}")
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(f"Error sending email: {e}")

    # Generate image directory
    image_directory = generate_plots(holdings)
    
    # Send email with the provided sender, recipient, and image directory
    send_email(sender, to, image_directory)

def email_per_user():
    directory = 'holdings'
    users = os.listdir(directory)
    # print(users)
    for user in users:
        with open("holdings/"+user, "r") as json_file:
            holdings = json.load(json_file)

        sender = "stocks@ajbeery.com"
        to = holdings["EMAIL"]
        del holdings['EMAIL']

        email_create(sender, to, holdings)
