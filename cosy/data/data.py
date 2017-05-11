"""
Module ...

@Author: 
@Date: 

"""

################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os
import sys
from datetime import datetime

import sqlite3 
#print "sqlite3 ", sqlite3.version, "run-time SQLite library version ",sqlite3.sqlite_version

# Import custom modules


################## Variables #################################### Variables #################################### Variables ##################

from global_config import * # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

from db_sql import db_data_sql


################## Functions ###################################### Functions ###################################### Functions ####################


# create database connection
def create_connection():
    """
    Create a database connection to the SQLite database specified by DB_PATH,DB_NAME
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    logging.debug('%s:%s: Create DB Connection to %s' % (script_file,func_name,DB_DATA))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,DB_DATA))
        return conn
    
    except Exception as e:
        logging.error('%s:%s: Could not create connection' % (script_file,func_name))
        raise e
    
    return None

# create table
def create_table(conn, create_table_sql) :
    """
    Create a table from the create_table_sql statement

    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    try:
        with conn:
            conn.execute(create_table_sql)
        
    except Exception as e:
        logging.error('%s:%s: Could not create table' % (script_file,func_name))
        raise e
    
    return True


def init_db():
    """
    Create database for cosy.
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial database' % (script_file,func_name))
    
    # connect to / create db
    conn = create_connection()
    
    # if connection possible
    if conn is not None:
        
        # iterate db_data_sql and create tables
        for create_table_sql in db_data_sql :
        
            # create projects table
            create_table(conn, create_table_sql)
    
        # Committing changes and closing the connection to the database file
        conn.commit()
        conn.close()
        
    else:
        print("Error! cannot create the database connection.")
        logging.error('%s:%s: Cannot create database connection.' % (script_file,func_name))
        return False

    return True










"""
# Never do this -- insecure!
symbol = 'RHAT'
c.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)

# Do this instead
t = ('RHAT',)
c.execute('SELECT * FROM stocks WHERE symbol=?', t)
print c.fetchone()

# Larger example that inserts many records at a time
purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
             ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
             ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
            ]
c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

Connection objects can be used as context managers that automatically commit or rollback transactions. In the event of an exception, the transaction is rolled back; otherwise, the transaction is committed:

import sqlite3

con = sqlite3.connect(":memory:")
con.execute("create table person (id integer primary key, firstname varchar unique)")

# Successful, con.commit() is called automatically afterwards
with con:
    con.execute("insert into person(firstname) values (?)", ("Joe",))

# con.rollback() is called after the with block finishes with an exception, the
# exception is still raised and must be caught
try:
    with con:
        con.execute("insert into person(firstname) values (?)", ("Joe",))
except sqlite3.IntegrityError:
    print "couldn't add Joe twice"


    
    
# example
def dbaccessexample():
    try:
        with db:
            db.execute('''INSERT INTO users(name, phone, email, password)
                    VALUES(?,?,?,?)''', (name1,phone1, email1, password1))
    except sqlite3.IntegrityError:
        print('Record already exists')
    except Exception as e:
        # Roll back any change if something goes wrong
        db.rollback()
        raise e
    finally:
        db.close()
    
"""