#!/usr/bin/python
# Required modules
# easy_install prettytable
# sendmail package
# Author: ahuang@liquidweb.com
# Last update: 2015-03-27

from prettytable import PrettyTable
import sqlite3
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
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

# connections per day in last 7 days
sqlTitle = "Connections per day in last 7 days"
cursor.execute("""
    SELECT strftime('%Y-%m-%d', connection_timestamp,'unixepoch') as 'Day', count(strftime('%m', connection_timestamp,'unixepoch')) as 'hits' 
    FROM connections 
    GROUP BY strftime('%Y', connection_timestamp,'unixepoch'), strftime('%m', connection_timestamp,'unixepoch'), strftime('%d', connection_timestamp,'unixepoch') 
    ORDER BY strftime('%Y', connection_timestamp,'unixepoch') DESC, strftime('%m', connection_timestamp,'unixepoch') DESC, strftime('%d', connection_timestamp,'unixepoch') DESC LIMIT 7
    """)
printTable(cursor, sqlTitle)

# most attacked ports (last 2 days)
sqlTitle = 'Most attacked port (last 2 days)'
cursor.execute("""
    SELECT strftime('%Y-%m-%d', connection_timestamp,'unixepoch') AS 'day', COUNT(local_port) AS hits, local_port AS port 
    FROM connections 
    WHERE connection_type = 'accept' 
    GROUP BY strftime('%Y', connection_timestamp,'unixepoch'), strftime('%m', connection_timestamp,'unixepoch'), strftime('%d', connection_timestamp,'unixepoch') 
    ORDER BY strftime('%Y', connection_timestamp,'unixepoch') DESC, strftime('%m', connection_timestamp,'unixepoch') DESC, strftime('%d', connection_timestamp,'unixepoch') DESC LIMIT 2;
    """)
printTable(cursor, sqlTitle)

# attacked ports (all time)
sqlTitle = "Most attacked ports (all time)"
cursor.execute("""SELECT COUNT(local_port) AS hits, local_port AS port 
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
    SELECT connection_protocol, datetime(connection_timestamp, 'unixepoch', 'localtime') as time, local_port, remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY ROUND((connection_timestamp%(3600*24))/3600)
    ORDER BY time DESC
    LIMIT 5
    """)
printTable(cursor, sqlTitle)

# top attack counts from remote host (last 2 days)
sqlTitle = "Top attacks from remote hosts (last 2 days)"
#    ORDER BY strftime('%Y', connection_timestamp,'unixepoch') DESC, strftime('%m', connection_timestamp,'unixepoch') DESC, strftime('%d', connection_timestamp,'unixepoch') DESC limit 2 
cursor.execute("""
    SELECT strftime('%Y-%m-%d', connection_timestamp,'unixepoch') AS day, COUNT(remote_host) AS hits, remote_host AS IP
    FROM connections 
    WHERE connection_type = 'accept' 
    GROUP BY strftime('%Y-%m-%d', connection_timestamp,'unixepoch') 
    ORDER BY strftime('%Y-%m-%d', connection_timestamp,'unixepoch') DESC 
    LIMIT 2;
    """)
printTable(cursor, sqlTitle)

# top attack counts from remote hosts (all time)
sqlTitle = "Top attacks from remote hosts (all time)"
cursor.execute("""
    SELECT COUNT(remote_host) AS hits, remote_host AS IP
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY strftime('%Y-%m-%d', connection_timestamp,'unixepoch')
    ORDER BY count(remote_host) DESC
    LIMIT 10
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
    SELECT COUNT(download_md5_hash) AS hits, download_md5_hash AS hash
    FROM downloads 
    GROUP BY download_md5_hash 
    ORDER BY COUNT(download_md5_hash) DESC
    LIMIT 20
    """)
printTable(cursor, sqlTitle)


# popular download locations
sqlTitle = "Popular download locations"
cursor.execute("""
    SELECT COUNT(*) AS hits, download_url
    FROM downloads
    GROUP BY download_url
    ORDER BY COUNT(*) DESC
    LIMIT 20
    """)
printTable(cursor, sqlTitle)

output.close()
conn.close()

# sending and variables for mail function
send_from = 'root@nospaceindent.com'
send_to = 'honeypot@liquidweb.com'
ip = getipaddr()
filename = 'export.txt'

send_mail(send_from, send_to, ip, filename)
