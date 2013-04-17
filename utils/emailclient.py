# -*- coding: utf-8 -*-
# Email client for EMailFeed

import getpass, imaplib, re, email
from email.parser import FeedParser
from email.header import decode_header

def get_mail(server, login, password):
    """Get email from Imap server"""

    M = imaplib.IMAP4(server)
    M.login(login, password)
    M.select()
    typ, data = M.search(None, 'ALL')

    email_re = re.compile(r"<.*?>")
    #print typ, data
    result = []
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        msg = FeedParser()
        msg.feed(data[0][1])
        msg.close()
        mail = email.message_from_string(data[0][1])
        from_ = mail.get('from', '')
        subject = decode_header(mail.get('subject', ''))[0][0]
        if mail.is_multipart():
            pp = mail.get_payload()
            for m in pp:
    #            print m
                if m.get_content_type() == "text/html":
                    p = m.get_payload(decode=True)
        else:
            p = mail.get_payload(decode=True)
        result.append({"from": from_, "subject": subject, "msg": p, "original_msg": data[0][1]})
        M.store(num, '+FLAGS', '\\Deleted')
    M.expunge()
    M.close()
    M.logout()
    return result

if __name__ == "__main__":
    for m in get_mail("tax26.com", "aba@tax26.com", "Nthvbyfnjh"):
        for k, v in m.iteritems():
            print k, ":", v
