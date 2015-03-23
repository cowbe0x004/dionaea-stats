#!/usr/bin/python

import sqlite3
import sys

db_file = '/var/dionaea/logsql.sqlite'

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def printCol(cursor):
    col_names = [cn[0] for cn in cursor.description]
    print "%-10s %s" % (col_names[0], col_names[1])
#    for col in col_names:
#        sys.stdout.write(col + " ")
#    print
#   print
    #col_names = list(map(lambda x: x[0], cursor.description))
    #print "%-10s %s" % (col_names[0], col_names[1])

def printRows(cursor):
    rows = cursor.fetchall()
    for col in rows:
        print '%-10d %s' % (col[0], col[1])

    print "\n+==================+"

# attacked ports
print "Attacked ports"
cursor.execute("""SELECT COUNT(local_port) AS hitcount, local_port AS port 
    FROM connections 
    WHERE connection_type = 'accept' 
    GROUP BY local_port 
    HAVING count(local_port) > 10
    """)

printCol(cursor)
printRows(cursor)

# latest attackers
print "Latest Attackers"
cursor.execute("""
    SELECT connection_protocol, ROUND((connection_timestamp%(3600*24))/3600) as hour, local_port, remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY ROUND((connection_timestamp%(3600*24))/3600)
    LIMIT 5
    """)
#printCol(cursor)
#printRows(cursor)

# attacks over a day
cursor.execute("""
    SELECT ROUND((connection_timestamp % (3600*24)) / 3600) AS hour, COUNT(*) AS hits
    FROM connections
    WHERE connection_parent IS NULL
    GROUP BY ROUND((connection_timestamp % (3600*24)) / 3600)
    """)
printCol(cursor)
printRows(cursor)

cursor.execute("""
    SELECT COUNT(download_md5_hash), download_md5_hash 
    FROM downloads 
    GROUP BY download_md5_hash 
    ORDER BY COUNT(download_md5_hash) DESC
    """)
printCol(cursor)
printRows(cursor)

# most attacks from remote hosts
cursor.execute("""
    SELECT COUNT(remote_host), remote_host
    FROM connections
    WHERE connection_type = 'accept'
    GROUP BY remote_host
    ORDER BY count(remote_host) DESC
    LIMIT 10
    """)
printCol(cursor)
printRows(cursor)

# popular download locations
cursor.execute("""
    SELECT COUNT(*) AS hits, download_url
    FROM downloads
    GROUP BY download_url
    ORDER BY COUNT(*) DESC
    """)
printCol(cursor)
printRows(cursor)

conn.close()
