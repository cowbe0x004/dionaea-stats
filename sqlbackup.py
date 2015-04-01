#!/usr/bin/python

import sqlite3
import shutil
import time
import os
import glob
import subprocess

# number of backups to keep
no_of_files = 8
# backup directory
backup_dir = 'backup'
# database file
db_file = 'data.db'
# dionaea init script
init_file = '/etc/init.d/dionaea'

# backup function
def backup_db(db_file, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # get the full name including path
    fullname = os.path.join(backup_dir, os.path.basename(db_file) + time.strftime("-%Y%m%d-%H%M%S"))

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("begin immediate")
    shutil.move(db_file, fullname)
    print("\nMoving {}...".format(fullname))
    conn.rollback()

    restart_dionaea(init_file)
    

# remove backup larger than number of backups to keep
def clean_data(backup_dir):
    print("\n--------------------------------------")
    print("Cleaning up old backups")

    path, dirs, files = os.walk(backup_dir).next()
    file_count = len(files)
        
    if file_count > no_of_files:
        oldest = min(glob.iglob(backup_dir + '/*'), key=os.path.getctime)
        if os.path.isfile(oldest):
            os.remove(oldest)
            print("Deleting {}...".format(oldest))


# empty database
def restart_dionaea(init_file):
    # restart dionea
    subprocess.call("/etc/init.d/dionaea restart", shell=True)

if __name__ == "__main__":
    backup_db(db_file, backup_dir )
    clean_data(backup_dir)

    print("\nBackup update has been successful.")
