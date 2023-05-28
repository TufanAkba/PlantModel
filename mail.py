#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tag is empty 
# Please cancel the if clause after filling the email data

import smtplib
import ssl
from email.message import EmailMessage


def mail(body):
    
    if True:
        pass
    else:
    # Fill this part!...
        # Define email sender and receiver
        email_sender = ''#fill the mail address
        email_password = ''#fill the password
        email_receiver = ''#fill the mail addresses to
        
        # Set the subject and body of the email
        subject = 'analyses completed!'
        if not body  :
            body = """
            simulation has done. Check pls.
            """
        
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        
        # Add SSL (layer of security)
        context = ssl.create_default_context()
        
        # Log in and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

if __name__ =='__main__':
    mail('')
