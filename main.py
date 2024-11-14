import subprocess

subprocess.check_call(["pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import json
from helpers_sendgrid import email_create

with open("holdings/holdings.json", "r") as json_file:
    holdings = json.load(json_file)

sender = "stocks@ajbeery.com"
to = holdings["EMAIL"]
del holdings['EMAIL']

email_create(sender, to, holdings)