"""Send bulk email to mail addresses listed in a file"""

# Setup
emailFrom    = "MDMM2018 <mdmm@mdmm.pl>"
emailSubject = "MDMM2018 - conference announcement"
filePlain    = "plain.txt"
fileRich     = "rich.html"
fileEmails   = "emails.txt"
mailServer   = "ssmtp.example.com"
mailUser     = "mdmm"
dryRun       = False
# End of setup

import smtplib
import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

userList = open(fileEmails).readlines()

msg = MIMEMultipart('alternative')
msg['Subject'] = emailSubject
msg['From'] = emailFrom
msg['To'] = ""

text = open(filePlain).read()
html = open(fileRich).read()

part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')
msg.attach(part1)
msg.attach(part2)

class Sender(object):

    def __init__(self, server, user, password, dry_run=False):

        self.dry_run = dry_run
        self.server = server
        self.user = user
        self.password = password

    def __enter__(self):
        if not self.dry_run:
            self.smtp = smtplib.SMTP(self.server, 587)
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.login(self.user, self.password)

    def __exit__(self):
        if not self.dry_run:
            self.smtp.quit()

    def send(self, msg):
        """Actually send the message or return text if dry run"""
        if not dryRun:
            self.smtp.send_message(msg)
        else:
            return msg.as_string()


if __name__ == '__main__':

    mailPassword = getpass.getpass("Enter mailbox password:")

    with Sender(mailServer, mailUser, mailPassword, dryRun) as snd:
        for u in userList:
            user = u.strip()
            print("Sending to", user, "...")
            msg.replace_header('To', u)
            out = snd.send(msg)
            if out: print(out)
