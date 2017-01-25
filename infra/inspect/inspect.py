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
INSPECT_DOAMINS = [ 'https://r2lab.inria.fr', 'http://r2lab.inria.fr', 'https://r2labapi.inria.fr',
                    'https://r2labapi.inria.fr:443/PLCAPI',
                    'https://onelab.eu/'
                  ]
SEND_RESULTS_TO = ['mario.zancanaro@inria.fr']

#DEFAUULTS
IP              = 'r2lab.inria.fr'
PORT            = 999
PROTOCOL        = 'https'

#GLOBALS
RESULTS = []

#PARAMS
parser = ArgumentParser()
parser.add_argument("-e", "--email", default=SEND_RESULTS_TO, dest="send_to", nargs='+',
                    help="Email to receive the execution results")
parser.add_argument("-fe", "--force_email", dest="force_email", nargs='+',
                    help="If not present the email will send only in errors are detected")
parser.add_argument("-D", "--domains", default=INSPECT_DOAMINS, dest="domains", nargs='+',
                    help="List of domains to check the answer header. Ex.: https://domain1.com http://domain2.com ...")

args    = parser.parse_args()
send_to = args.send_to
domains = args.domains
force_e = args.force_email

#TO DEAL WITH NO ANSWER AFTER x SECONDS TRYING CONNECT SIDECAR
import signal
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)



def main():
    inspect_sites(domains)

    #CUSTOMIZED TESTS
    sidecar_socket(IP, PORT)
    sidecar_emit(IP, PORT, 'https')
    # branch_set_in_faraday()
    #----------------------

    send = False
    for res in RESULTS:
        if res['bug'] or force_e:
            send = True
            break
    if send:
        send_email(send_to, send)



def inspect_sites(domains):
    """ check some URL  """
    for domain in domains:
        bug = False
        try:
            r   = requests.head(domain)
            ans = r.status_code
            dt  = None
            if str(ans)[0] == '4' or str(ans)[0] == '5':
                bug = True
        except Exception as e:
            ans = '---'
            dt  = e
        RESULTS.append({'service' : domain, 'ans': ans, 'details': dt, 'bug': bug})



def sidecar_socket(ip=IP, port=PORT):
    """ check if a socket is answering in domain : port """
    import socket
    s = socket.socket()
    try_emit = True
    try:
        a = s.connect((ip, port))
        RESULTS.append({'service' : 'sidecar in <b>{}</b> port <b>{}</b>'.format(ip, port), 'ans': 'UP', 'details': '', 'bug': False})
    except Exception as e:
        try_emit = False
        RESULTS.append({'service' : 'sidecar in <b>{}</b> port <b>{}</b>'.format(ip, port), 'ans': '---', 'details': e, 'bug': True})
    finally:
        s.close()



def sidecar_emit(ip=IP, port=PORT, protocol=PROTOCOL):
    """ check if we can exhange messages with sidecar """
    url = "{}://{}:{}/".format(protocol,ip,port)
    channel = 'info:nodes'
    #sys.path.insert(0, r'/home/mzancana/Documents/inria/r2lab/sidecar/')
    sys.path.insert(0, r'/root/r2lab/sidecar/')
    from sidecar_client import connect_url

    infos = {'id': 0, 'available' : 'ok'}
    try:
        with timeout(seconds=5):
            print('INFO: trying connect...')
            socketio = connect_url(url)
            socketio.emit(channel, json.dumps(infos), None)
            RESULTS.append({'service' : 'messages emit in <b>{}</b> on <b>{}</b>'.format(channel, url), 'ans': 'UP', 'details': '', 'bug': False})
    except Exception as e:
        print('INFO: NO connection...')
        RESULTS.append({'service' : 'messages emit in <b>{}</b> on <b>{}</b>'.format(channel, url), 'ans': '---', 'details': e, 'bug': True})



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



def send_email(emails, send=True):
    body = email_body()
    body = body.replace("[THE DATE]", date('%d/%m/%Y - %HH'))
    body = body.replace("[THE CONTENT]", content())
    title = 'Inspect Routine of {}'.format(date('%d/%m/%Y - %HH'))

    try:
        #try a copy of the email
        f = open('inspect.html', 'w')
        f.write(body)
        f.close()
    except Exception as e:
        pass
    if send:
        fire_email("root@faraday.inria.fr", emails, title, body)



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
    main()
