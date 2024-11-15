docker build -t stock-tracker .

Run Docker image using

docker run -d -e SENDGRID_API_KEY=YOUR-API-KEY-FROM-SENDGRID stock-tracker

when starting, you will need to create a venve, create holdings_real.json, and set sendgrid api key ans a env variable.
export VARIABLE_NAME="value"
