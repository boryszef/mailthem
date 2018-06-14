from mailThem import Message
import unittest
import re
from sys import argv


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.fromaddr = "me@example.com"
        self.toaddr = "you@example.net"
        self.subject = "Blah blah"
        self.bodyplain = "Hello,\nBye"
        self.bodyhtml = """<html>
        <body>
        <p>Hello,</p>
        <p>Bye <img src="logo.jpg" /></p>
        </body>
        </html>"""

    def test_from(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain)
        txt = msg.as_string()
        result = re.search("^From: (.*)$", txt, re.M)
        self.assertTrue(result)
        self.assertEqual(result.group(1), self.fromaddr)

    def test_single_to(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain)
        txt = msg.as_string()
        result = re.search("^To: (.*)$", txt, re.M)
        self.assertTrue(result)
        self.assertEqual(result.group(1), self.toaddr)

    def test_multiple_to(self):
        to = ['a@b.com', 'b@c.com', 'd@e.com']
        msg = Message(self.fromaddr, to, self.subject,
                      self.bodyplain)
        txt = msg.as_string()
        result = re.search("^To: (.*)$", txt, re.M)
        self.assertTrue(result)
        self.assertEqual(result.group(1), ", ".join(to))

    def test_subject(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain)
        txt = msg.as_string()
        result = re.search("^Subject: (.*)$".format(self.subject), txt, re.M)
        self.assertTrue(result)
        self.assertEqual(result.group(1), self.subject)

    def test_no_body(self):
        with self.assertRaises(RuntimeError):
            Message(self.fromaddr, self.toaddr, self.subject)

    def test_plain(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain)
        txt = msg.as_string()
        result = re.search("^Content-Type: text/plain;", txt, re.M)
        self.assertTrue(result)

    def test_html(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      bodyhtml=self.bodyhtml)
        txt = msg.as_string()
        result = re.search("^Content-Type: text/html;", txt, re.M)
        self.assertTrue(result)

    def test_plain_and_html(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain, self.bodyhtml)
        txt = msg.as_string()
        result = re.search("^Content-Type: multipart/alternative;", txt, re.M)
        self.assertTrue(result)

    def test_attach_image(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain, self.bodyhtml, ['logo.jpg'])
        txt = msg.as_string()
        result = re.search("^Content-Type: image/jpeg", txt, re.M)
        self.assertTrue(result)
        result = re.search("^Content-ID: <image\d+>", txt, re.M)
        self.assertTrue(result)

    def test_attach_script(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain, self.bodyhtml, [argv[0]])
        txt = msg.as_string()
        result = re.search("^Content-Type: text/x-python", txt, re.M)
        self.assertTrue(result)

    def test_two_attachments(self):
        msg = Message(self.fromaddr, self.toaddr, self.subject,
                      self.bodyplain, self.bodyhtml, ['logo.jpg', argv[0]])
        txt = msg.as_string()
        print(txt)
        pattern = re.compile("^Content-Disposition: attachment;")
        count = 0
        for match in pattern.finditer(txt, re.M):
            count += 1
        self.assertEqual(count, 2)


if __name__ == '__main__':
    unittest.main()
