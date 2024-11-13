
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='andrewjosephbeery@gmail.com',
    to_emails='andrewjbeery@gmail.com',
    subject='Another Test',
    html_content='Lets go')
try:
    sg = SendGridAPIClient(os.environ.get('sendgrid_api_key'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)