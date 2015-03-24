#!/usr/bin/python
# easy_install prettytable

from prettytable import PrettyTable
import sqlite3
import sys

db_file = '/var/dionaea/logsql.sqlite'

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def printTable(cursor):
    col_names = [cn[0] for cn in cursor.description]
    rows = cursor.fetchall()
    
    colNum = len(col_names)
    x = 0

    y = PrettyTable()
    y.padding_wdith = 1
    while x < colNum:
        y.add_column(col_names[x], [row[x] for row in rows])
        y.align[col_names[x]] = "c"
        x = x + 1
    
#    y.align[col_names[1]] = "r"
    print(y)
    print
    
# printing column names
#def printCol(cursor):
#    col_names = [cn[0] for cn in cursor.description]
#    print "%-10s %s" % (col_names[0], col_names[1])
#    #col_names = list(map(lambda x: x[0], cursor.description))
#    #print "%-10s %s" % (col_names[0], col_names[1])
#
#def printRows(cursor):
#    rows = cursor.fetchall()
#    for col in rows:
#        print '%-10d %s' % (col[0], col[1])

# attacked ports
print "Attacked ports"
cursor.execute("""SELECT COUNT(local_port) AS hitcount, local_port AS port 
    FROM connections 
    WHERE connection_type = 'accept' 
    GROUP BY local_port
    HAVING count(local_port) > 10
    ORDER BY COUNT(local_port) DESC
    """)
printTable(cursor)

# latest attackers
print "Latest Attackers"
cursor.execute("""
    SELECT connection_protocol, datetime(connection_timestamp, 'unixepoch') as time, local_port, remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY ROUND((connection_timestamp%(3600*24))/3600)
    ORDER BY time DESC
    LIMIT 5
    """)
printTable(cursor)

# attacks over a day
print "Attacks over a day"
cursor.execute("""
    SELECT ROUND((connection_timestamp % (3600*24)) / 3600) AS hour, COUNT(*) AS hits
    FROM connections
    WHERE connection_parent IS NULL
    GROUP BY ROUND((connection_timestamp % (3600*24)) / 3600)
    """)
printTable(cursor)

# popular malware downloads
print "Popular malware downloads"
cursor.execute("""
    SELECT COUNT(download_md5_hash), download_md5_hash 
    FROM downloads 
    GROUP BY download_md5_hash 
    ORDER BY COUNT(download_md5_hash) DESC
    """)
printTable(cursor)

# most attacks from remote hosts
print "Most attacks from remote hosts"
cursor.execute("""
    SELECT COUNT(remote_host), remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY remote_host
    ORDER BY count(remote_host) DESC
    LIMIT 10
    """)
printTable(cursor)

# popular download locations
print "Popular download locations"
cursor.execute("""
    SELECT COUNT(*) AS hits, download_url
    FROM downloads
    GROUP BY download_url
    ORDER BY COUNT(*) DESC
    """)
printTable(cursor)

conn.close()
