import hashlib
import json
import requests
from urllib.parse import urlencode

# Define the user's credentials
username = "will"
password = "will"

# Hash the password using MD5
hashed_password = hashlib.md5(password.encode()).hexdigest()
print('hashedPassword:', hashed_password)

# Define the POST data for the login request
post_data = {
    "method": "login",
    "input_type": "JSON",
    "response_type": "JSON",
    "rest_data": json.dumps({
        "user_auth": {
            "user_name": username,
            "password": hashed_password,
        },
    }),
}

# Convert 'post_data' to a URL-encoded query string
query_string = urlencode(post_data)

# Set the headers
headers = {"Content-Type": "application/x-www-form-urlencoded"}

# Authenticate with SuiteCRM
crm_url = "http://192.168.1.116/suitcrm/service/v4_1/rest.php"  # Replace with your CRM URL
response = requests.post(crm_url, data=query_string, headers=headers)

if response.status_code == 200:
    sessionID = response.json().get("id")
    print("Session ID:", sessionID)
else:
    print("Error:", response.status_code, response.text)
