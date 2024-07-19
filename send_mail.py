from dotenv import load_dotenv
import os
import sys
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.utils import make_msgid
from email.utils import formatdate
from email.utils import formataddr
from email import encoders
import chardet
import csv
import re
import json
import time

# Loading environment keys
load_dotenv()
MY_EMAIL = os.getenv('MY_EMAIL')
PASSWORD_KEY= os.getenv('PASSWORD_KEY')
SENDER_NAME = os.getenv('SENDER_NAME')

# Uncomment the below line to also add CC
CC_RECIPIENTS = [('Name 1', 'email 1'),('Name 2','email 2')]

def get_server_address(email_provider: str):
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)
        smtp_server = data['providers'][email_provider]['smtp']
        port = data['providers'][email_provider]['port']
    
    return (smtp_server, port)

def create_mail_server(email_provider):
    # SMTP Server and port number
    server_address, port  = get_server_address(email_provider)
    zoho_server= server_address
    zoho_port= port

    if email_provider == 'zoho':
        my_server = smtplib.SMTP(zoho_server, zoho_port)
    else:
        my_server = smtplib.SMTP_SSL(zoho_server, zoho_port)
    
    # my_server.set_debuglevel(1)
    my_server.ehlo()
    my_server.starttls() # It was not working for gmail. It was working for zoho
    my_server.ehlo()
    my_server.login(MY_EMAIL,PASSWORD_KEY)
    print(f"From Email: {MY_EMAIL}")

    return my_server

def send_mail(msg, my_server):
    try:
        recipients = [msg['To']] + [email for _, email in CC_RECIPIENTS]
        my_server.sendmail(msg['From'], recipients, msg.as_string())
        print(f"Mail successfully sent to {msg['To']} at {msg['Date']}")
    except Exception as e:
        print(f"Mail NOT sent to {msg['To']}: {e}")

def make_mail(to_address, candidate_name, subject, body, format, image_path = None, file_path = None, video_path = None):
    msg = MIMEMultipart("alternative")

    msg['To'] = formataddr((candidate_name, to_address))
    msg['From'] = formataddr((SENDER_NAME, MY_EMAIL))
    msg["Subject"] = subject
    msg['Message-Id'] = make_msgid()
    msg['Date'] = formatdate(localtime=True)
    msg.attach(MIMEText(body, 'plain' if format == 'plain' else 'html'))

    msg['Cc'] = ', '.join([formataddr((name, email)) for name, email in CC_RECIPIENTS])

    if image_path:
        img_attachment = open(image_path, 'rb').read()
        msg.attach(MIMEImage(img_attachment, name=os.path.basename(image_path)))

    # Attach video file
    if video_path:
        with open(video_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {video_path}')
        msg.attach(part)

    if file_path:
        with open(file_path, 'rb') as f:
            file = MIMEApplication(
                f.read(),
                name=os.path.basename(file_path)
            )
            file.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(file_path))
            # file['Content-Disposition'] = f'attachment'
            # filename="{os.path.basename(resume_file)}"
            msg.attach(file)

    return msg 

def get_email_text(file_path):
    # identify the encoding of the text file
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)['encoding']

    with open(file_path, 'r', encoding = encoding) as file:
        file_contents = file.read()

    # Selects between : and .
    sub_pattern = r':(.*?)\.'
    sub_match = re.search(sub_pattern, file_contents)

    if sub_match:
        subject = sub_match.group(1)  # The content of the first capturing group
    else:
        subject = ""

    # Define the regex pattern to match everything after the first newline
    body_pattern = r'\n(.*)'
    body_match = re.search(body_pattern, file_contents, re.DOTALL)

    if body_match:
        text_content = body_match.group(1)
    else:
        text_content = ""
    
    return (subject, text_content)


if __name__=="__main__":

    # Ensure there are exactly 4 arguments (including the script name)
    print("\n---- PROGRAM START -----\n")
    if len(sys.argv) != 5:
        print("Usage: python send_mail.py <email_provider> <email_content_file.txt> <receiver.csv> <email_mode>")
        sys.exit(1)
    
    email_provider = sys.argv[1]
    email_content_file = sys.argv[2]
    receiver_email_ids = sys.argv[3]
    email_mode = sys.argv[4]  #html, plain
    
    my_server = create_mail_server(email_provider)

    subject, text_content = get_email_text(email_content_file)

    with open(receiver_email_ids) as csv_file:
        jobs = csv.reader(csv_file)
        next(jobs)  # Skip header row
        
        for candidate_name, candidate_email in jobs:
            
            email_text=text_content.format(candidate_name=str(candidate_name))
            mail = make_mail(str(candidate_email), str(candidate_name), subject, email_text, email_mode) #, 'attachments/me.JPG', 'attachments/test.xlsx', 'attachments/video.mp4')

            send_mail(mail, my_server)
            time.sleep(10)  # Sleep is to stop multiple requests at once. 
    res = my_server.quit()
    print(res)

    print("\n---- PROGRAM END -----\n")