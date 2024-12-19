#!/bin/bash
# Wait until ngrok has started
while ! curl --silent --head --fail http://localhost:4040/status; do
  echo "Waiting for ngrok to start..."
  sleep 2
done

# Fetch the public ngrok URL
ngrok_url=$(curl --silent http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

# Print the ngrok URL or save it to a file
echo "Ngrok public URL: $ngrok_url"
# Save the URL to a file, for example:
echo $ngrok_url > /path/to/save/ngrok_url.txt
