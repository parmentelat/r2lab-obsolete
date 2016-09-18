#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The nightly script used to monitor all the R2lab on a nightly basis
and outline the ones that are not reliable
"""

from argparse import ArgumentParser
import os
import os.path
from datetime import datetime
import time
import sys
import re
import json
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger




WEEKDAY_STAT = "sunday"
phases       = {}




def main():
    """ Execute the load for all nodes in Faraday. """

    parser = ArgumentParser()
    parser.add_argument("-N", "--nodes", dest="nodes", default="all",
                        help="Comma separated list of nodes")
    parser.add_argument("-a", "--avoid", dest="avoid_nodes",
                        help="Comma separated list of nodes to avoid")
    parser.add_argument("-V", "--version", default="fedora-23.ndz", dest="version",
                        help="O.S version to load")
    parser.add_argument("-t", "--text-dir", default="/root/r2lab/nightly/", dest="text_dir",
                        help="Directory to save text file")
    parser.add_argument("-e", "--email", default="fit-r2lab-users@inria.fr", dest="send_to_email",
                        help="Email to receive the execution results")
    #parser.add_argument("-d", "--days", dest="days", default=['wed','sun'],
    #                    help="Comma separated list of weekday to run")
    args = parser.parse_args()

    # # in function of the given days it will or not skip run
    # # and empty list will run always
    # days         = args.days if type(args.days) is list else args.days.split(',')
    # days         = list(map(lambda x: x.lower(), days))
    send_to_email  = args.send_to_email
    nodes          = args.nodes
    version        = args.version
    avoid_nodes    = args.avoid_nodes
    dir_name       = args.text_dir
    nodes          = format_nodes(nodes, avoid_nodes)
    all_nodes      = name_node(nodes)
    send_results_to= [str(send_to_email)] #default in args send_to_email: fit-r2lab-users@inria.fr

    # if not should_i_run(days):
    #     print "INFO: none of the informed days match with the current. Let's skip and exit..."
    #     exit(0)

    for node in nodes:
        create_phases_db(node)

    print "INFO: {}".format(now())

    #=========================================
    # TURN ON ALL NODES ======================
    print "INFO: turn on nodes"
    all_nodes = name_node(nodes)
    cmd = command_in_curl(all_nodes, 'on')
    results = execute(cmd)
    if error_presence(results):
        print "ERROR: turn on not executed"
    else:
        print "INFO: nodes turned on"

    for node in nodes:
        cmd = command_in_curl([name_node(node)])
        result = execute(cmd)
        stdout = remove_special_char(result['node']['stdout']).strip()
        if stdout.lower() in ['already on', 'on']:
            update_phases_db(node, 1)


    #=========================================
    # LOAD THE NEW OS ON NODES ===============
    print "INFO: execute load on nodes"
    results    = {}
    all_nodes = stringfy_list(all_nodes)
    cmd = "rhubarbe-load {} -i {}; ".format(all_nodes, version)
    result = execute(cmd, key='node')
    if error_presence(result):
        print "ERROR: one or more node were not loaded correctly. CMD and result logs below:"
        print cmd
        print "-----"
        print result
        print "-----"
    else:
        stdout = remove_special_char(result['node']['stdout'])
        #==================================================================
        #searching in the answer of the command for the sentence of success
        #+058s: fit23 Uploading successful
        #+058s: <node> Uploading successful
        nodes_found = parse_results_from_load(stdout)
        update_phases_db(nodes_found, 2)


    #=========================================
    # CHECK ZOMBIE (not turn off) NODES ======
    print "INFO: given some time to recover OS info from loaded nodes"
    wait_and_update_progress_bar(45)
    print "INFO: check for zombie nodes"
    all_nodes = name_node(nodes)
    cmd = command_in_curl(all_nodes, 'off')
    results = execute(cmd)
    if error_presence(results):
        print "ERROR: turn off not executed"
    else:
        print "INFO: nodes turned off"

    wait_and_update_progress_bar(30)
    all_nodes   = to_str(nodes)
    results     = {}

    for node in all_nodes:
        cmd = "curl reboot{}/status;".format(node)
        result = execute(cmd, key=node)
        results.update(result)

        if error_presence(result):
            pass
        else:
            status = remove_special_char(result[node]['stdout']).strip()
            if status.lower() in ['already off', 'off']:
                update_phases_db(node, 3)


    #=========================================
    # RESULTS  ===============================
    print "INFO: summary of reset routine"
    failed_nodes = []
    for key, value in sorted(phases.iteritems()):
        if value['ph1'] == 'ko' or value['ph2'] == 'ko' or value['ph3'] == 'ko':
            failed_nodes.append(key)
        failed_nodes = list(set(failed_nodes))

        print "  node:  #{} ".format(key)
        print " start:   {} ".format(value['ph1'])
        print "  load:   {} ".format(value['ph2'])
        print "zombie:   {} ".format(value['ph3'])
        print "--"
    print " "

    print "INFO: setting round red bullets for nodes with issues"
    set_node_status(range(1,38),  'ok')
    set_node_status(failed_nodes, 'ko')

    print "INFO: send email"
    summary_in_mail(failed_nodes, send_results_to)

    print "INFO: write in file"
    #this is the old file containing all info since we start nightly
    write_in_file(failed_nodes, "nightly.txt", dir_name)

    print "INFO: write in file in new format"
    save_data_in_txt (phases, "nightly_data.txt",  dir_name)
    save_data_in_json(phases, "nightly_data.json", dir_name)

    print "INFO: end of main"
    print "INFO: {}".format(now())




def should_i_run(days):
    """ check if the current day matches the list of days to decide or not run """
    from datetime import date
    import calendar
    today = date.today()
    # will run by default
    if days is None or not days:
        return True
    #once a weekday is given, lets check is is the current one
    else:
        week_day = calendar.day_abbr[today.weekday()]
        return week_day.lower() in days




def parse_results_from_load(text):
    """ return a list of the nodes found in the log/answer from load commmand """
    text    = text.lower()
    search  = "uploading successful"
    idxs    = [n for n in xrange(len(text)) if text.find(search, n) == n]
    back_in = 7 #fit02 is 5 + two spaces use it on split
    split_by= ' '
    found   = []

    for idx in idxs:
        found.append(text[idx-back_in : idx].split(split_by)[1])

    found = map(lambda each:each.strip("fit"), found)
    found = list(set(found))

    return found




def update_phases_db(node, the_phase):
    """ unset fail for the node n in the phase """
    if not type(node) is list:
        try:
            phases[int(node)]["ph{}".format(the_phase)] = 'ok'
        except Exception as e:
            print '-- ERROR: node {} is NOT in the list!'.format(node)
    else:
        for n in node:
            try:
                phases[int(n)]["ph{}".format(the_phase)] = 'ok'
            except Exception as e:
                print '-- ERROR: node {} is NOT in the list!'.format(n)




def create_phases_db(node):
    """ create the phases to register each step of nightly routine """
    number_of_phases = 3
    all_phases = {}
    for n in range(number_of_phases):
        all_phases["ph{}".format(n+1)] = 'ko'

    phases.update({int(node) : all_phases})




def parse_phases_db_in_style(phase_result):
    """ parsing the result to css layout """
    new_phase = ""

    #in regular case
    if phase_result is "ok":
        new_phase = '32px Arial, Tahoma, Sans-serif; color: #42c944;">&#8226;'
    #in fail case
    elif phase_result is "ko":
        new_phase = '18px Arial, Tahoma, Sans-serif; color: red;">&#215;'

    return new_phase




def write_in_file(text, the_file, dir_name):
    """save the results in a file for posterior use of it """
    dir_name  = dir_name
    file_name = the_file

    text = ', '.join(str(x) for x in text)

    with open(os.path.join(dir_name, file_name), "a") as fl:
        fl.write("{}: {}\n".format(date(),text))




def save_data_in_txt(results, the_file, dir_name, answer='short'):
    """save the results in a file for posterior use of it """
    dir_name  = dir_name
    file_name = the_file
    number_of_phases = 3
    all_nodes = ''
    for node in results:
        fail   = False
        text   = ''
        failed = ''
        for ph in range(number_of_phases):
            if results[node]["ph{}".format(ph+1)] is 'ko':
                failed = failed + map_phases(ph+1,answer)
                fail = True

        if fail:
            text = text + str(node) + '('+failed+')'
            all_nodes = all_nodes + text +', '
    all_nodes = all_nodes[:-2]

    with open(os.path.join(dir_name, file_name), "a") as fl:
        fl.write("{}: {}\n".format(date(),all_nodes))




def summary_in_mail(nodes, send_results_to):
    """send a summary output of the routine"""
    list_of_bug_nodes = nodes
    title = ''
    body  = ''
    to    = send_results_to

    line_ok = ''
    line_fail = ''
    lines_fail = ''

    header = '\
            <tr>\n \
            <td style="width: 40px; text-align: center;"></td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/power.png" style="width:25px;height:25px;">&nbsp;start&nbsp;</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/share.png" style="width:25px;height:25px;">load</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/zombie.png" style="width:25px;height:25px;">zombie</td>\n \
            <td>&nbsp;&nbsp;</td>\n \
            </tr>'

    for node in sorted(list_of_bug_nodes):
        line_fail = '\
                    <tr>\n \
                        <td style="font:15px helveticaneue, Arial, Tahoma, Sans-serif;"><span style="border-radius: 50%; border: 2px solid #525252; width: 30px; height: 30px; line-height: 30px; display: block; text-align: center;"><span style="color: #525252;">{}</span></span></td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td></td>\n \
                    </tr>\
                    '.format(node, parse_phases_db_in_style(phases[int(node)]['ph1']), parse_phases_db_in_style(phases[int(node)]['ph2']), parse_phases_db_in_style(phases[int(node)]['ph3']))
        lines_fail += line_fail

    legend = '\
            <tr>\n \
                <td colspan="7"><br></td>\n \
            </tr>\n \
            <tr>\n \
            <td style="font:9px helveticaneue, Arial, Tahoma, Sans-serif;">\n \
                <span style="color: #525252;">\n \
                &nbsp;<b>start:</b> <br>\n \
                &nbsp;<b>load:</b>  <br>\n \
                &nbsp;<b>zombie:</b><br>\n \
            </span>\n \
            </td>\n \
            <td colspan="6" style="font:9px helveticaneue, Arial, Tahoma, Sans-serif;">\n \
                <span style="color: #525252;">\n \
                &nbsp; node successfully started at the beginning of the routine check.<br>\n \
                &nbsp; the load command successfully completed.<br>\n \
                &nbsp; node cannot be switched off at the end of the test.<br>\n \
                </span>\n \
            </td>\n \
            </tr>\
            '
    lines_fail = header + lines_fail + legend

    line_ok = '\
            <tr>\n \
                <td style="font:11px Arial, Tahoma, Sans-serif; width: 10px; text-align: left;"><img src="http://r2lab.inria.fr/assets/img/people.png" style="width:35px;height:35px;"></td>\n \
                <td colspan="9" style="font:14px Arial, Tahoma, Sans-serif; vertical-align: middle; text-align: left;"><b>Great!</b><span style="font:12px Arial"> All nodes are working fine!</span></td>\n \
            </tr>\n \
            '

    body = email_body()
    body = body.replace("[THE DATE]", date('%d/%m/%Y'))

    if len(list_of_bug_nodes) < 1:
        body = body.replace("[THE CONTENT]", line_ok)
        title = 'Nightly Routine of {}: Perfect!'.format(date('%d/%m/%Y'))

    elif len(list_of_bug_nodes) >= 1:
        body = body.replace("[THE CONTENT]", lines_fail)
        title = 'Nightly Routine of {}: Issues!'.format(date('%d/%m/%Y'))

    # cmd = 'mail -a "Content-type: text/html" -s "{}" {} <<< "{}"'.format(title, to, body)
    # result = execute(cmd)
    send_email("root@faraday.inria.fr", to, title, body)




def email_body():
    """ just a durty partial body """

    #with open('_nightly_email.html', 'r') as email_partial:
    #    body = email_partial.read()

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
            <td colspan="10">The nightly routine summary<sup style="font:9px Arial, Tahoma, Sans-serif; color: red;"><b> beta</b></sup></td>\n \
    			</tr>\n \
          <tr>\n \
            <td colspan="10"><br></td>\n \
          </tr>\n \
          [THE CONTENT]\n \
    		</table>\n \
            {}\n \
      </body>\n \
    </html>'.format(get_statistic(WEEKDAY_STAT))
    return body




def send_email(sender, receiver, title, content):
    """ send email using python """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject']  = title
    msg['From']     = sender
    msg['To']       = ", ".join(receiver)

    # Record the MIME types of both parts - text/plain and text/html.
    body = MIMEText(content, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(body)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()




def set_node_status(nodes, status='ok'):
    """ Inform status page in r2lab.inria.fr the nodes with problem """
    from socketIO_client import SocketIO, LoggingNamespace
    hostname = 'r2lab.inria.fr'
    port     = 443

    infos = [{'id': arg, 'available' : status} for arg in nodes]

    socketio = SocketIO(hostname, port, LoggingNamespace)
    # print("Sending {infos} onto {hostname}:{port}".format(**locals()))
    socketio.emit('chan-status', json.dumps(infos), None)




def command_in_curl(nodes, action='status'):
    """ Transform the command to execute in CURL format """
    nodes = number_node(nodes)

    in_curl = map(lambda x:'curl reboot'+str('0'+str(x) if x<10 else x)+'/'+action, nodes)
    in_curl = '; '.join(in_curl)

    return in_curl




def to_str(list_items):
    """ Change the integer array to string array """
    if not type(list_items) is list:
        raise Exception("invalid parameter: {}, must be a list".format(list_items))
        return False

    new_list = (map(str, list_items))

    return new_list




def wait_and_update_progress_bar(wait_for):
    """ Print the progress bar when waiting for a while """
    for n in range(wait_for):
        time.sleep(1)
        print '\b.',
        sys.stdout.flush()
    print ""




def execute(command, host_name='localhost', host_user='root', key='node'):
    """ Execute the command in host """
    ec = ExperimentController()

    node = ec.register_resource("linux::Node")
    ec.set(node, "hostname", host_name)
    ec.set(node, "username", host_user)
    ec.set(node, "cleanExperiment", True)
    ec.set(node, "cleanProcesses", False)
    ec.set(node, "cleanProcessesAfter", False)
    ec.deploy(node)

    app = ec.register_resource("linux::Application")
    ec.set(app, "command", command)
    ec.register_connection(app, node)
    ec.deploy(app)
    ec.wait_finished(app)

    stdout    = remove_special_char(ec.trace(app, "stdout"))
    exitcode  = remove_special_char(ec.trace(app, 'exitcode'))

    results = {}
    results.update({ str(key) : {'exitcode' : exitcode, 'stdout' : stdout}})

    return results




def error_presence(results):
    """ Check error mentions in output or 1 in exit code """
    err_words = ['error', 'errors', 'fail']
    error = False

    for result in results:
        stdout    = remove_special_char(results[result]['stdout'])
        exitcode  = remove_special_char(results[result]['exitcode'])

        if exitcode is '':
            exitcode = 1

        if set(err_words).intersection(stdout.split()) or int(exitcode) > 0:
            error = True
            break

    return error




def stringfy_list(list):
    """ Return the list in a string comma separated ['a,'b','c'] will be a,b,c """
    stringfy_list = ','.join(list)

    return stringfy_list




def remove_special_char(str):
    """ Remove special caracters from a string """
    if str is not None:
        new_str = str.replace('\n', ' ').replace('\r', ' ').replace('\"', ' ').lower()
        #new_str = re.sub('[^A-Za-z0-9]+', ' ', str)
    else:
        new_str = ''

    return new_str




def number_node(nodes):
    """ Returns the number from the node alias [fitXX] """
    if type(nodes) is list:
        ans = []
        for node in nodes:
            node_temp = int(node.lower().replace('fit', ''))
            ans.append(node_temp)
    else:
        ans = int(nodes.lower().replace('fit', ''))

    return ans




def name_node(nodes):
    """ Returns the name from the node alias [fitXX] """
    if type(nodes) is list:
        ans = []
        for node in nodes:
            if int(node) < 10:
                node = str(node).rjust(2, '0')

            ans.append('fit'+str(node))
    else:
        if int(nodes) < 10:
            nodes = str(nodes).rjust(2, '0')

        ans = 'fit'+str(nodes)

    return ans




def all_nodes():
    """Range of all nodes in faraday """
    nodes = range(1,38)
    nodes = map(str, nodes)
    for k, v in enumerate(nodes):
        if int(v) < 10:
            nodes[k] = v.rjust(2, '0')

    return nodes




def new_list_nodes(nodes):
    """Put nodes in string list format with zero left """
    if not type(nodes) is list:
        if ',' in nodes:
            nodes = nodes.split(',')
        elif '-' in nodes:
            nodes = nodes.strip("[]").split('-')
            nodes = range(int(nodes[0]), int(nodes[1])+1)
        else:
            nodes = [nodes]

    new_list_nodes = map(str, nodes)
    for k, v in enumerate(new_list_nodes):
        if int(v) < 10:
            new_list_nodes[k] = v.rjust(2, '0')

    return new_list_nodes




def format_nodes(nodes, avoid=None):
    """Correct format when inserted 'all' in -N nodes parameter """
    to_remove = avoid

    if 'all' in nodes:
        nodes = all_nodes()
    else:
        nodes = new_list_nodes(nodes)

    if to_remove:
        to_remove = new_list_nodes(to_remove)
        nodes = [item for item in nodes if item not in to_remove]

    return nodes




def save_data_in_json(results, the_file, dir_name):
    """ Save the result in a json file """
    dir = dir_name
    file_name = the_file
    number_of_phases = 3
    all_nodes = {}
    for node in results:
        for ph in range(number_of_phases):
            if results[node]["ph{}".format(ph+1)] is 'ko':
                try:
                    all_nodes[str(node)].update( { "ph{}".format(ph+1) : 'ko'} )
                except Exception as e:
                    all_nodes.update( {str(node) : { "ph{}".format(ph+1) : 'ko'}} )

    all_nodes = parse_ph_to_names(all_nodes)
    temp_results = {"date" : str(date()), "data" : all_nodes}

    with open(os.path.join(dir, file_name), "a") as js:
        js.write(json.dumps(temp_results)+"\n")




def parse_ph_to_names(dict_json):
    """ Change the phase names ph1, ph2, ph3, ph4... to names: t, s, l, o, z """
    temp_json = json.dumps(dict_json)
    temp_json = temp_json.replace("\"ph1\"", "\"t\"")
    temp_json = temp_json.replace("\"ph2\"", "\"l\"")
    temp_json = temp_json.replace("\"ph3\"", "\"z\"")
    return json.loads(temp_json)




def map_phases(phase, answer='short'):
    """ gives a human name for each phase instead of ph1, ph2, ...
        BE CAREFUL(`s` and `o` are not here but they are in DB because it was used)
        t=start s=ssh l=load o=o.s.changed z=zombie
    """
    normal_human_name = ['', 'start', 'load', 'zombie']
    short_human_name  = ['', 't',     'l',    'z'     ]
    # just in case of giveen 'ph1' as phase
    if type(phase) is str:
        phase = phase.replace('ph', '')
    if   answer is 'short':
        new_name = short_human_name[int(phase)]
    elif answer is 'normal':
        new_name = normal_human_name[int(phase)]
    else:
        new_name = normal_human_name[int(phase)]

    return new_name




def split(array, size):
    """ split one array in n (size) other parts """

    splited_arrays = []

    while len(array) > size:
        pice = array[:size]
        splited_arrays.append(pice)
        array = array[size:]
    splited_arrays.append(array)

    return splited_arrays




def now():
    """ Current datetime """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




def date(format='%Y-%m-%d'):
    """ Current date (2016-04-06)"""
    return datetime.now().strftime(format)




def historic_file_in_array():
    """read db file from nightly and put in array format. Returns ['2016-01-22: 27, 09, 29', '2016-01-23: 27',...] """
    dir_name  = "/root/r2lab/nightly/"
    file_name = "nightly.txt"
    with open(dir_name+file_name) as f:
        lines = f.read().splitlines()
    return lines




def treat_historic_file(data):
    """split in single array the dates and nodes from the nightly file. Data must be ['2016-01-22: 27, 09, 29', '2016-01-23: 27',...] """
    chars_to_remove = [':', ',']
    #all dates summarized iin one array
    date = []
    #all nodes summarized iin one array
    node = []

    for line in data:
        line = line.translate(None, ''.join(chars_to_remove))
        line = line.split()
        date.append(line[0])
        del line[0]
        node.append(line)
    node = reduce(lambda c, x: c + x, node, [])
    return node




def generate_graph(data_nodes, nodes=None):
    """generate each node graph. data_nodes param come from treat_historic_file func. """
    lines = ''
    if nodes is None:
        nodes = range(1,38)
    back_color = '#ffb1b1'
    data_nodes = map(int, data_nodes)
    table_width = 600
    final_with  = table_width + 30 #the first and last collunm widht sum
    total = len(historic_file_in_array())

    header = '\n \
    <br>\n \
    <hr>\n \
    <table cellspacing="1" style="padding: 10px;">\n \
        <tr>\n \
          <td colspan="3">The weekly statistic summary<sup style="font:9px Arial, Tahoma, Sans-serif; color: red;"><b> beta</b></sup></td>\n \
        </tr>\n \
        <tr>\n \
          <td colspan="3"><br></td>\n \
        </tr>\n \
        <tr style="width:630px; display: block;">\n \
          <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: left;"><img src="http://r2lab.inria.fr/assets/img/graph.png"/ style="width:35px;height:35px;"></td>\n \
          <td colspan="2" style="font:14px Arial, Tahoma, Sans-serif; vertical-align: middle; text-align: left;"><span style="font:12px Arial"> Failed nodes since <b>22/01/2016</b>.</span></td>\n \
        </tr>\n \
        <tr><td colspan=3><br></td>\n \
        </tr>\n \
    '

    line = '<tr style="width:{}px; display: block;">\n \
              <td style="font: 9px sans-serif; text-align: left; width: 15px;">[NODE]</td>\n \
              <td style="font: 9px sans-serif; border-right: 0px solid #9e9d9d; border-bottom: 0px solid #9e9d9d; border-top: 0px solid #9e9d9d; border-left: 1px solid #9e9d9d; background-color: {}; text-align: right; padding: 0px; color: black; height: 5px; width: [WIDTH]px;"></td>\n \
              <td style="font: 9px sans-serif; border-right: 1px solid #9e9d9d; border-bottom: 0px dashed #9e9d9d; border-top: 0px dashed #9e9d9d; border-left: 0px; background-color: white; text-align: right; padding: 0px; color: black; height: 5px; width: [DIFF WIDTH]px;"></td>\n \
              <td style="font: 9px sans-serif; text-align: left; width: 15px;">&nbsp;[PERCENT]%</td>\n \
            </tr>\n \
            '.format(final_with, back_color)

    footer = '</table>'

    for node in nodes:
        value = data_nodes.count(node)
        percent = int(round((value*100)/total))
        diff_percent = 100 - percent
        width = percent * (table_width/100)
        diff_width = table_width - 100 - width
        temp_line = line.replace("[NODE]", str(node))
        temp_line = temp_line.replace("[DIFF WIDTH]", str(diff_width))
        temp_line = temp_line.replace("[WIDTH]", str(width))
        temp_line = temp_line.replace("[PERCENT]", str(percent))

        if (percent > 0):
            lines = lines + temp_line

    return header+lines+footer




def get_statistic(the_day="monday"):
    """ get the graph each given weekday  """
    from datetime import date
    import calendar
    graph = ''

    today = date.today()
    week_day = calendar.day_name[today.weekday()]
    if week_day.lower() == the_day.lower():
        h = historic_file_in_array()
        d = treat_historic_file(h)
        graph = generate_graph(d)

    return graph




if __name__ == "__main__":
    main()
