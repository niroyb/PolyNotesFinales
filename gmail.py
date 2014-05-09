#!/usr/bin/python
# -*- coding: utf-8 -*-

import smtplib
import email
from email.mime.text import MIMEText


class Gmail:
    def __init__(self, user_address, password):
        self.user = user_address
        self.password = password

    def send_message(self, to_address, subject, message_html):
        msg = self.__new_message(to_address, subject)
        msg.attach(MIMEText(message_html, 'html'))
        self.__send_msg(msg, to_address)

    def send_message_to_self(self, subject, message):
        self.send_message(self.user, subject, message)

    def __new_message(self, to_address, subject):
        msg = email.MIMEMultipart.MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = to_address
        msg['Subject'] = subject
        return msg

    def __send_msg(self, msg, to_address):
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.user, to_address, msg.as_string())
        server.quit()
