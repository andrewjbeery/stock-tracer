docker build -t stock-tracker .

Run Docker image using

docker run -d \
  --restart unless-stopped \
  -e SENDGRID_API_KEY=apikey \
  stock-tracker

when starting, you will need to create a venve, create holdings_real.json, and set sendgrid api key ans a env variable.
export VARIABLE_NAME="value"

api key is stored in github gist
