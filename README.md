# Stock Tracker Setup

This guide will help you set up the Stock Tracker using Docker on your Linux Machine.

## Initial Setup
Before starting the container, you'll need to complete a few setup steps:

### Create a Virtual Environment (venv):

Make sure you have Python installed.
Create and activate a virtual environment in your project directory.
```bash
python3 -m venv venv
source venv/bin/activate
```
### Create the holdings_real.json file:

This file will store your stock holdings data. Ensure it is placed in the holdings directory you'll mounted to the Docker container. It should be in this format:

```json
{
    "EMAIL": "recipient@example.com",
    "AAPL" : 500,
    "Goog" : 500,
    "eric" : 305.549
}
```

### Set the SendGrid API Key:

The SendGrid API key should be set as an environment variable.
```bash
export SENDGRID_API_KEY="your_sendgrid_api_key"
```
Retrieve the API Key:

My API key is stored in a GitHub Gist. You can get yours through sendgrid.

## Building the Docker Image

To build the Docker image for the Stock Tracker, run the following command:

```bash
docker build -t stock-tracker .
```
## Running the Docker Container
Once the image is built, you can run the container with the following command:

```bash
docker run -d \
  --restart unless-stopped \
  -v /path/to/holdings/directory:/app/holdings \
  -e SENDGRID_API_KEY=your_api_key \
  stock-tracker
```
/path/to/holdings/directory: Replace this with the actual path to the directory where you want to store the holdings.

your_api_key: Replace this with your SendGrid API key.

