docker build -t stock-tracker .

Run Docker image using

docker run -d \
  --restart unless-stopped \
  -v path_to_holdings_directory:/app/holdings \
  -e SENDGRID_API_KEY=api_key \
  stock-tracker

when starting, you will need to create a venve, create holdings_real.json, and set sendgrid api key ans a env variable.
export VARIABLE_NAME="value"

api key is stored in github gist
