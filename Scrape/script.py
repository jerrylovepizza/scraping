from datetime import datetime
import json
from fierceBiotech import fierceBioTech
from scrapeSites import scrapeSites
from endpts import endpts
import os
import openpyxl as xl
from openpyxl.styles import Font

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

import schedule
from time import sleep
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import numpy as np
import csv

def sendGridEmail(table, sender, receiver, key):
    message = Mail(
        from_email=sender,
        to_emails=[receiver, "sg0000075@gmail.com"],
        subject='Last Week News :' + datetime.now().strftime("%Y-%m-%d %H:%M"),
        html_content=table)
    try:
        sg = SendGridAPIClient(key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def makeTable(websites, results):
    
    table = ""
    
    table = "<table>"
    table += "<thead><tr style='text-align: center; font-weight: bold;'><td style='border: 1px solid #dddddd;width: 170px;'>Company</td><td style='border: 1px solid #dddddd;'>Title</td><td style='border: 1px solid #dddddd;'>Url</td></tr></thead>"
    table += "<tbody>"
    
    allNames = []
    
    bfirst = True
    
    for x in websites:
        bfirst = True
        rowcount = 0

        for row in results:
            if (row[1] == x["name"]):
                if bfirst:
                    table += "<tr><td style='border: 1px solid #dddddd;' rowspan='#!num!#'>" + row[1]+ "</td><td  style='border: 1px solid #dddddd;'><p style='height: 16px; overflow: hidden;display: inline-block; margin:0;padding:0;'>" + row[2]+ "</p></td><td style='border: 1px solid #dddddd;'><a style='height: 16px; overflow: hidden;display: inline-block;' href='" + row[3] + "'>" + row[3]+ "</a></td></tr>"
                    bfirst = False
                else:
                    table += "<tr><td  style='border: 1px solid #dddddd;'><p style='height: 16px; overflow: hidden;display: inline-block; margin:0;padding:0;'>" + row[2]+ "</p></td><td style='border: 1px solid #dddddd;'><a style='height: 16px; overflow: hidden;display: inline-block;' href='" + row[3] + "'>" + row[3]+ "</a></td></tr>"
                rowcount += 1
        if bfirst:
            table += "<tr><td style='border: 1px solid #dddddd;'>" + x["name"] + "</td><td colspan='2' style='text-align: center;border: 1px solid #dddddd;'>None</td></tr>"
        else:
            table = table.replace("#!num!#", str(rowcount))
        

    # Names = []
    # for x in websites:
    #     if x["name"] not in allNames:
    #         Names.append(x["name"])
    
    # table += "<tr><td style='border: 1px solid #dddddd;'>" + "<br>".join(Names) + "</td><td colspan='3' style='text-align: center;border: 1px solid #dddddd;'>No Results</td></tr>"
    # table +="</tbody></table>"
    # table = table.replace("#!num!#", str(rowcount)).replace("#!content!#", "<br>".join(allNames))
    
    return table

def job():
    with open("config.json") as f:
        data = json.loads(f.read().strip())

    days = data["days"]
    websites = data["websites"]
    sender = data["sender"]
    receiver = data["receiver"]    
    sendgrid_key = data["sendgrid"]

    results = []
    results += endpts(websites, days)
    results += fierceBioTech(websites, days)
    results += scrapeSites(websites, days)    
    table = makeTable(websites, results)
    sendGridEmail(table, sender, receiver, sendgrid_key)

job()

schedule.every().friday.at("13:00").do(job)

while True:
    schedule.run_pending()
    sleep(20)
