"""Send bulk email to mail addresses listed in a file"""

# Setup
emailFrom    = "John Doe <doe@example.com>"
emailSubject = "[MDMM2018] Announcement"
fileEmails   = "emails.txt"
filePlain    = "plain.txt"
fileRich     = "rich.html"
attachments  = ['logo.jpg']
mailServer   = "smtp.example.com"
mailUser     = "robot"
dryRun       = False
# End of setup

import smtplib
import getpass
import mimetypes
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE
from collections import namedtuple

MType = namedtuple('MType', ['type', 'encoding', 'maintype', 'subtype'])

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
            attachment_types[att] = MType(ctype, encoding, maintype, subtype)

        if bodyplain:
            text = MIMEText(bodyplain, _subtype='plain', _charset='UTF-8')

        if bodyhtml:
            image_cid = {}
            idx = 0
            for aname, atypes in attachment_types.items():
                if atypes.maintype != 'image': continue
                cid = "image{}".format(idx)
                idx += 1
                pattern = 'src\s*=\s*"{}"'.format(aname)
                substitute = 'src="cid:{}"'.format(cid)
                bodyhtml = re.sub(pattern, substitute, bodyhtml,
                                  re.IGNORECASE|re.MULTILINE)
                image_cid[aname] = cid
            html = MIMEText(bodyhtml, _subtype='html', _charset='UTF-8')

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

        for atname,attype in attachment_types.items():
            if attype.maintype == 'image':
                with open(atname, 'rb') as atfile:
                    atm = MIMEImage(atfile.read(), _subtype=attype.subtype)
                    if atname in image_cid:
                        cid = image_cid[atname]
                        atm.add_header('Content-ID', '<{}>'.format(cid))
            elif attype.maintype == 'text':
                with open(att) as atfile:
                    atm = MIMEText(atfile.read(), _subtype=attype.subtype)
            else:
                raise NotImplementedError(
                    "{} attachments are not implemented".format(attype.ctype))
            atm.add_header('Content-Disposition', 'attachment',
                           filename=atname)
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
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.dry_run:
            self.smtp.quit()

    def send(self, msg):
        """Actually send the message or return text if dry run"""
        if not dryRun:
            self.smtp.send_message(msg)
        else:
            return msg.as_string()


if __name__ == '__main__':

    mailPassword = getpass.getpass("Enter mailbox password: ")

    with open(fileEmails) as fp:
        recp_list = [ x.strip() for x in fp.readlines() ]

    with open(filePlain) as fp:
        bodyplain = fp.read()

    with open(fileRich) as fp:
        bodyhtml = fp.read()

    with Sender(mailServer, mailUser, mailPassword, dryRun) as snd:
        msg = Message(emailFrom, '', emailSubject, bodyplain, bodyhtml,
                      attachments)
        for recp in recp_list:
            print("Sending to", recp, "...")
            msg.replace_header('To', recp)
            out = snd.send(msg)
