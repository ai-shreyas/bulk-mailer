## Bulk-Mailer

This program sends emails to multiple recipients at once. It retrieves email addresses and names from an Excel file and uses an email template from a text file.

In most of the cases your normal email and password won't work if you have 2 factor authentication enabled. 

For gmail you need app password which you can generate using this link: https://myaccount.google.com/apppasswords

For Zoho, go to settings and create an App password.

Also, you need to know the smptp server address and port number of your email provider.

Listed below are SMTP server and PORT number for few popular email providers:


<h3>Gmail: </h3>
<p>SMTP - smtp.gmail.com <br> PORT - 465</p>

<h3>Zoho: </h3>
<p>SMTP - smtppro.zoho.in <br> PORT - 587</p>

## Usages
- Create a .env following the format of env.example
- Run the below command from the root directory
```
python send_mail.py <email_provider> <email_content_file.txt> <receiver.csv> <email_mode>
```
Argument details:

- email_provider -> A string specifying your email provider (Example - 'zoho', 'gmail'). If you plan to use any other provider, you need to put the details in the config.json file.
- email_content_file.txt -> Content of your email. See sample_email.txt
- receiver.csv -> All the receiver email ids in csv format. See example receivers.csv
- email_mode -> 'html' or 'plain'



### Side Note
- This can be easily adapted to work with any email provider. Make changes in the config.json file.
- Be aware of the rate limit imposed by your email service provider. Do not send more than 50 emails at a time, otherwise your email service provider might block you tinking DOS attack.
- Attachments can also be send. See make_mail method and make adjustment. 

### To do 
- Efficient error handling
- Support multiple email providers.
- More customisations

### Useful Reference Links:

- https://mailtrap.io/blog/python-send-email-gmail/#:~:text=To%20send%20an%20email%20with%20Python%20via%20Gmail%20SMTP%2C%20you,Transfer%20Protocol%20(SMTP)%20server.

