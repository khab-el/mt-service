from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from src.settings import settings


async def send(mail_client: SMTP, email, email_message, email_subject="mail from tradebot support", email_message_type='plain', attach=None):
    message = MIMEMultipart()
    message['From'] = settings.SMTP_FROM
    message['To'] = email
    message['Subject'] = email_subject
    message.attach(MIMEText(email_message, email_message_type))
    if attach:
        strategy_file = MIMEApplication(await attach['Body'].read())
        strategy_file.add_header('Content-Disposition', 'attachment', filename='strategy.ex5')
        message.attach(strategy_file)
    text = message.as_string()
    await mail_client.connect()
    await mail_client.login(settings.SMTP_FROM, settings.SMTP_FROM_PASSWORD)
    await mail_client.sendmail(settings.SMTP_FROM, email, text)
    await mail_client.quit()
