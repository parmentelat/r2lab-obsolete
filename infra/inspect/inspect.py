import requests
from argparse import ArgumentParser
import os
import os.path
from datetime import datetime
import time
import sys
import subprocess
from subprocess import Popen
import re
import json
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from urllib.parse import urlparse

#GLOBALS PARAMS
INSPECT_SITES   = [ 'https://r2lab.inria.fr', 'http://r2lab.inria.fr', 'https://r2labapi.inria.fr',
                    'https://r2labapi.inria.fr:443/PLCAPI', 'http://r2labapi.inria.fr:443/PLCAPI',
                    'https://onelab.eu/'
                  ]
SEND_RESULTS_TO = ['mario.zancanaro@inria.fr']

#GLOBALS
RESULTS = []

def inspect_sites():
    """ check some URL  """
    sites = INSPECT_SITES
    for site in sites:
        try:
            r   = requests.head(site)
            ans = r.status_code
            dt  = None
            if ans == 400 or ans == 404:
                bug = True
            else:
                bug = False
        except Exception as e:
            ans = '---'
            dt  = e
            bug = True
        RESULTS.append({'service' : site, 'ans': ans, 'details': dt, 'bug': bug})


def sidecar_socket():
    """ check if a socket is answering in domain : port """
    import socket
    port = 999
    ip   = 'r2lab.inria.fr'
    s    = socket.socket()
    try:
        s.connect((ip, port))
        RESULTS.append({'service' : 'sidecar in {} port {}'.format(ip, port), 'ans': 'UP', 'details': '', 'bug': False})
    except Exception as e:
        RESULTS.append({'service' : 'sidecar in {} port {}'.format(ip, port), 'ans': '---', 'details': e, 'bug': True})
    finally:
        s.close()


def sidecar_connect(nodes, status='ko'):
    """ check if we can exhange messages with sidecar """
    from socketIO_client import SocketIO, LoggingNamespace
    ip   = 'r2lab.inria.fr'
    port = 999

    infos = [{'id': arg, 'available' : status} for arg in nodes]

    socketio = SocketIO(ip, port, LoggingNamespace)
    socketio.emit('info:nodes', json.dumps(infos), None)


def branch_set_in_faraday():
    """ check if the branch setted in faraday is PUBLIC """
    command = "cd /root/r2lab/; git branch | grep \* | cut -d ' ' -f2"
    # command = "cd /home/mzancana/Documents/inria/r2lab/; git branch | grep \* | cut -d ' ' -f2"
    ans_cmd = run(command)
    if not ans_cmd['status'] or ans_cmd['output'] != 'public':
        RESULTS.append({'service' : 'faraday branch', 'ans': '---', 'details': ans_cmd['output'], 'bug': True})
    else:
        RESULTS.append({'service' : 'faraday branch', 'ans': ans_cmd['output'], 'details': '', 'bug': False})


def content():
    content = ''
    header  = '\
            <tr>\n \
                <td colspan=2 style="font:13px Arial, Tahoma, Sans-serif; text-align: left; color: black;"><b>STATUS</b></td>\n \
                <td style="font:13px Arial, Tahoma, Sans-serif; text-align: left;"><b>URL/SERVICE</b></td>\n \
                <td></td>\n \
            </tr>'

    for res in RESULTS:
        if res['bug']:
            line  = '\
                    <tr>\n \
                        <td style="font:25px Arial, Tahoma, Sans-serif; width: 20px; text-align: left; color: {};">&#8226;</td>\n \
                        <td style="font:12px Arial, Tahoma, Sans-serif; width: 15%; text-align: left; color: {};">{}</td>\n \
                        <td style="font:12px Arial, Tahoma, Sans-serif; text-align: left;"><b>{}</b><br>error: {}</td>\n \
                        <td></td>\n \
                    </tr>\
                    '.format(map_color(str(res['ans'])), map_color(str(res['ans'])), res['ans'], res['service'], res['details'])
        else:
            line  = '\
                    <tr>\n \
                        <td style="font:25px Arial, Tahoma, Sans-serif; width: 20px; text-align: left; color: {};"">&#8226;</td>\n \
                        <td style="font:12px Arial, Tahoma, Sans-serif; width: 15%; text-align: left; color: {};"">{}</td>\n \
                        <td style="font:12px Arial, Tahoma, Sans-serif; text-align: left;">{}</td>\n \
                        <td></td>\n \
                    </tr>\
                    '.format(map_color(str(res['ans'])), map_color(str(res['ans'])), res['ans'], res['service'])
        content += line
    return header+content


def send_email():
    body = email_body()
    body = body.replace("[THE DATE]", date('%d/%m/%Y - %HH'))
    body = body.replace("[THE CONTENT]", content())
    title = 'Inspect Routine of {}'.format(date('%d/%m/%Y - %HH'))

    # f = open('/user/mzancana/home/Documents/inria/check.html', 'w')
    # f.write(body)
    # f.close()
    send = False
    for res in RESULTS:
        if res['bug']:
            send = True
            break
    if send:
        fire_email("root@faraday.inria.fr", SEND_RESULTS_TO, title, body)


def run(command, std=True):
    """ run the commands
    """
    if std:
        p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    (out, err) = p.communicate()
    ret        = p.wait()
    out        = out.strip().decode('ascii')
    err        = err
    ret        = True if ret == 0 else False
    return dict({'output': out, 'error': err, 'status': ret})


def map_color(code):
    "set color for an answer"
    color = 'green'

    if code[0] == '3':
        color = '#ed7a1c'
    elif code == '200' or code == 'OK':
        color = 'green'
    elif code[0] == '4' or code == '---':
        color = 'red'
    return color


def fire_email(sender, receiver, title, content):
    """ send email """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart('alternative')
    msg['Subject']  = title
    msg['From']     = sender
    msg['To']       = ", ".join(receiver)

    body = MIMEText(content, 'html')
    msg.attach(body)
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()


def email_body():
    """ just a durty partial body """

    body = '<!DOCTYPE html>\n \
    <html lang="en">\n \
      <head>\n \
        <meta charset="utf-8">\n \
        <meta http-equiv="X-UA-Compatible" content="IE=edge">\n \
      </head>\n \
      <body style="font:14px helveticaneue, Arial, Tahoma, Sans-serif; margin: 0;">\n \
      	<table style="padding: 10px;">\n \
    		  <tr>\n \
            <td colspan="10" style="align: left;"><h5><span style="background:#f0ad4e; color:#fff; padding:4px; border-radius: 5px;">[THE DATE]</span></h5></td>\n \
        	</tr>\n \
          <tr>\n \
            <td colspan="10">The inspect routine</td>\n \
    			</tr>\n \
          <tr>\n \
            <td colspan="10"><br></td>\n \
          </tr>\n \
          [THE CONTENT]\n \
    		</table>\n \
      </body>\n \
    </html>'
    return body


def date(format='%Y-%m-%d'):
    """ Current date (2016-04-06)"""
    return datetime.now().strftime(format)


if __name__ == "__main__":
    inspect_sites()
    # sidecar_connect([15])
    branch_set_in_faraday()
    sidecar_socket()
    send_email()
