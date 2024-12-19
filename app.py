from flask import Flask, request, jsonify
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path to the holdings directory
HOLDINGS_DIR = os.path.join(os.getcwd(), 'holdings')

# Ensure holdings directory exists
os.makedirs(HOLDINGS_DIR, exist_ok=True)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json  # Expecting JSON payload
    email = data.get('email')
    stocks = data.get('stocks')

    if not email or not stocks:
        return jsonify({"error": "Email and stocks are required"}), 400

    # Transform the data into the desired format
    transformed_data = {"EMAIL": email}

    # Add each stock ticker and holdings to the transformed_data
    for ticker, holdings in stocks.items():
        transformed_data[ticker] = holdings

    # Save user data in a JSON file named after the email
    file_path = os.path.join(HOLDINGS_DIR, f"{email.replace('@', '_at_')}.json")
    with open(file_path, 'w') as file:
        json.dump(transformed_data, file)

    return jsonify({"message": "Data saved successfully!"})

if __name__ == '__main__':
    app.run(port=5000)
