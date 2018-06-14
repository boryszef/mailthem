"""Send bulk email to mail addresses listed in a file"""

# Setup
emailFrom    = "MDMM2018 <mdmm@mdmm.pl>"
emailSubject = "MDMM2018 - conference announcement"
filePlain    = "plain.txt"
fileRich     = "rich.html"
fileEmails   = "emails.txt"
attachments  = []
mailServer   = "ssmtp.example.com"
mailUser     = "mdmm"
dryRun       = False
# End of setup

import smtplib
import getpass
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE

userList = open(fileEmails).readlines()

text = open(filePlain).read()
html = open(fileRich).read()


class Message(MIMEMultipart):

    def __init__(self, fromaddr, toaddr, subject, bodyplain=None,
                 bodyhtml=None, attachments=[]):

        super(Message, self).__init__()
        self['Subject'] = subject
        self['From'] = fromaddr
        if isinstance(toaddr, str):
            toaddr = [toaddr]
        self['To'] = COMMASPACE.join(toaddr)
        self.preamble = 'This is a multi-part message in MIME format.'

        attachment_types = {}
        for att in attachments:
            ctype, encoding = mimetypes.guess_type(att)
            if ctype is None:
                raise RuntimeError("Could not guess the MIME type")
            maintype, subtype = ctype.split('/', 1)
            attachment_types[att] = (ctype, encoding, maintype, subtype)

        if bodyplain:
            text = MIMEText(bodyplain, 'plain')

        if bodyhtml:
            image_cid = {}
            for att in attachment_types:
                if att[2] != 'image': continue
                reference = re.search("src=\"({})\"".format(att), bodyhtml,
                                       re.I|re.M)
                if reference:
                    print(reference)
            html = MIMEText(bodyhtml, 'html')

        if bodyplain and bodyhtml:
            alternative = MIMEMultipart('alternative')
            alternative.attach(text)
            alternative.attach(html)
            self.attach(alternative)
        elif bodyplain:
            self.attach(text)
        elif bodyhtml:
            self.attach(html)
        else:
            raise RuntimeError("plain text or html message must be present")

        for attname,atttype in attachment_types.items():
            break
            with open(att) as atm_file:
                atm = MIMEText(atm_file.read(), _subtype=subtype)
                atm.add_header('Content-Disposition', 'attachment',
                               filename=att)
                self.attach(atm)


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
            msg = Message(emailFrom, u, emailSubject, bodyplain)
            out = snd.send(msg)
            if out: print(out)
