#!/usr/bin/python
# easy_install prettytable

from prettytable import PrettyTable
import sqlite3
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
import smtplib
import socket

# opening sqlite db and cursor
db_file = '/var/dionaea/logsql.sqlite'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# saving output to file
with open('export.txt', 'w') as output:
    # empty content from previous run
    output.truncate()

# printing the data
def printTable(cursor, sqlTitle):
    # get column names from description
#    col_names = list(map(lambda x: x[0], cursor.description))
    col_names = [cn[0] for cn in cursor.description]
    rows = cursor.fetchall()
    
    colNum = len(col_names)
    x = 0

    y = PrettyTable()
    # get all columns
    while x < colNum:
        y.padding_width = 1
        y.add_column(col_names[x], [row[x] for row in rows])
        y.align[col_names[0]] = "c"
        x = x + 1

    print sqlTitle
    print(y)
    print
    # output as html
#    outputData = y.get_html_string()
    outputData = y.get_string()

    # saving output to file
    with open("export.txt", "a") as output:
        output.write(sqlTitle + "\n")
        output.write(outputData + "\n\n\n")
        output.close()

# sending data to email
def send_mail(send_from, send_to, ip, filename, server="localhost"):
    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Reports for Dionaea on %s" % ip

    # attaching html file
#    part = MIMEText(file(filename).read(), 'html')
#    msg.attach(part)

    # if only attaching text file
    msg.attach(MIMEText(file(filename).read()))

    mailer = smtplib.SMTP(server)
    mailer.sendmail(send_from, send_to, msg.as_string())
    mailer.close()

def getipaddr():
    return socket.gethostbyname(socket.gethostname())

# attacked ports
sqlTitle = "Attacked ports"
cursor.execute("""SELECT COUNT(local_port) AS hitcount, local_port AS port 
    FROM connections 
    WHERE connection_type = 'accept' 
    GROUP BY local_port
    HAVING count(local_port) > 10
    ORDER BY COUNT(local_port) DESC
    """)
printTable(cursor, sqlTitle)

# latest attackers
sqlTitle = "Latest Attackers"
cursor.execute("""
    SELECT connection_protocol, datetime(connection_timestamp, 'unixepoch') as time, local_port, remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY ROUND((connection_timestamp%(3600*24))/3600)
    ORDER BY time DESC
    LIMIT 5
    """)
printTable(cursor, sqlTitle)

# attacks over a day
sqlTitle = "Attacks over a day"
cursor.execute("""
    SELECT ROUND((connection_timestamp % (3600*24)) / 3600) AS hour, COUNT(*) AS hits
    FROM connections
    WHERE connection_parent IS NULL
    GROUP BY ROUND((connection_timestamp % (3600*24)) / 3600)
    """)
printTable(cursor, sqlTitle)

# popular malware downloads
sqlTitle = "Popular malware downloads"
cursor.execute("""
    SELECT COUNT(download_md5_hash), download_md5_hash 
    FROM downloads 
    GROUP BY download_md5_hash 
    ORDER BY COUNT(download_md5_hash) DESC
    """)
printTable(cursor, sqlTitle)

# most attacks from remote hosts
sqlTitle = "Most attacks from remote hosts"
cursor.execute("""
    SELECT COUNT(remote_host), remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY remote_host
    ORDER BY count(remote_host) DESC
    LIMIT 10
    """)
printTable(cursor, sqlTitle)

# popular download locations
sqlTitle = "Popular download locations"
cursor.execute("""
    SELECT COUNT(*) AS hits, download_url
    FROM downloads
    GROUP BY download_url
    ORDER BY COUNT(*) DESC
    """)
printTable(cursor, sqlTitle)

output.close()
conn.close()

# sending and variables for mail function
send_from = 'root@nospaceindent.com'
send_to = 'honeypot@liquidweb.com'
ip = getipaddr()
filename = 'export.txt'

#send_mail(send_from, send_to, ip, filename)
