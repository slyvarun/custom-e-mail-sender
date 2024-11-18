from flask import Flask, request, jsonify
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai

app = Flask(__name__)

# OpenAI API key
openai.api_key = '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'

# SMTP server configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SENDER_EMAIL = 'esports.kprit@gmail.com'
SENDER_PASSWORD = 'xkrezjoguhrmqubc'

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False

def generate_email_content(template, user_data):
    # Use OpenAI GPT model to customize the email content
    prompt = template.replace("{{name}}", user_data['name'])  # Replace placeholders
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",  # or "gpt-4" based on your plan
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

@app.route('/send-emails', methods=['POST'])
def send_emails():
    csv_file = request.files['csvFile']
    email_template = request.form['emailTemplate']

    if not csv_file or not email_template:
        return jsonify({"message": "CSV file and email template are required!"}), 400

    # Read CSV file
    df = pd.read_csv(csv_file)

    success_count = 0
    failure_count = 0

    for index, row in df.iterrows():
        user_data = {'name': row['Name'], 'email': row['Email']}  # Modify based on your CSV structure
        email_content = generate_email_content(email_template, user_data)

        if send_email(user_data['email'], "Your Custom Subject", email_content):
            success_count += 1
        else:
            failure_count += 1

    return jsonify({
        "message": f"Emails sent: {success_count}, Failed: {failure_count}"
    })

if __name__ == '__main__':
    app.run(debug=True)
