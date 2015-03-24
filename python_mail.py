#!/usr/bin/python

import smtplib

sender = 'andrew@nospaceindent.com'
receivers = ['andrew@nospaceindent.com']

message = """From: From Person <andrew@nospaceindent.com>
TO: To Person <andrew@nospaceindent.com>
Subject: SMTP testing

This is a test.
"""

try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message)
    print "Successfully sent email"
except smtplib.SMTPException:
    print "Error: unable to send email"
