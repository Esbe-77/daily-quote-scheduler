import smtplib
import json
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Get email credentials from environment variables
EMAIL_ADDRESS = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Load quotes from JSON file
json_file_path = "stoic_quotes.json"  # Update path if necessary

try:
    with open(json_file_path, "r") as file:
        stoic_quotes = json.load(file)
except FileNotFoundError:
    print(f"Error: {json_file_path} not found.")
    exit(1)

# Select 3 random Stoic quotes
random_quotes = random.sample([q["quote"] for q in stoic_quotes], 1)

# Email content
subject = "Todays' thought"
body = "\n\n".join(f"- {quote}" for quote in random_quotes)

# Function to send email
def send_email():
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Error: Missing email credentials. Ensure they are set in the .env file.")
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)

# Execute the function
send_email()
