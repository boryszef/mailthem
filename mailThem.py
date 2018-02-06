#!/usr/bin/python3

# Setup
emailFrom    = "MDMM2018 <mdmm@mdmm.pl>"
emailSubject = "MDMM2018 - conference announcement"
filePlain    = "plain.txt"
fileRich     = "rich.html"
fileEmails   = "emails.txt"
mailServer   = "ssmtp.example.com"
mailUser     = "mdmm"
mailPassword = "1234567890"
dryRun       = False
# End of setup

import smtplib

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

if not dryRun:
    s = smtplib.SMTP(mailServer, 587)
    s.ehlo()
    s.starttls()
    s.login(mailUser, mailPassword)

for u in userList:
    user = u.strip()
    print("Sending to", user, "...")
    msg.replace_header('To', u)
    if not dryRun: s.send_message(msg)
    else: print(msg.as_string())
if not dryRun: s.quit()
