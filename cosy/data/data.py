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

# define working database for module
db = DB_DATA

# get database definition dict
from db_sql import DATABASES

script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################


# create database connection
def create_connection():
    """
    Create a database connection to the SQLite database specified by DB_PATH,DB_NAME
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create DB Connection to %s' % (script_file,func_name,db))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,db))
        return conn
    
    except Exception as e:
        logging.error('%s:%s: Could not create connection' % (script_file,func_name))
        raise e
    
    return None



def insert_data(user_id, table, json):
    """
    Insert or Replace data.
    returns True on create
    > user ID, json
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert or Replace data to table: %s' % (script_file,func_name,table))
    
    try :
        # initial conditions
        insert_val_list = []
        
        ## build field list
        
        # initial conditions
        insert_fields = ""
        
        # dynamic fields/values
        for key,val in DATABASES[db][table]['vfields'].iteritems() :
            insert_fields += "%s, " % key
        
        # static fields/values
        insert_fields += "%s, " % 'last_date'
        insert_fields += "%s, " % 'user_id'
        
        # end field statement
        insert_fields = insert_fields[:-2] # loses ', ' from end of sql fields list
        
        ## build insert values from json
        for api_json in json:
            
            # initial conditions
            insert_values = []
            
            # dynamic fields/values
            for key,val in DATABASES[db][table]['vfields'].iteritems() :
                insert_values.append(api_json.get(key,None))
            
            # static fields/values
            insert_values.append(datetime.now())
            insert_values.append(user_id)
            
            # stack to detail list
            insert_val_list.append(tuple(insert_values))
            
        # build insert holder based on values
        insert_holder = "?, " * len(insert_values)
        
        # connect to / create db
        conn = create_connection()
        
        # connection object as context manager
        with conn:
            conn.executemany("INSERT OR REPLACE INTO {tn}({tf}) VALUES ({ih})".format(tn=table,tf=insert_fields,ih=insert_holder[:-2]),insert_val_list)
            
        #### Test
        for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
            print row
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        raise e
        return False

    except sqlite3.OperationalError as e:
        # connection object will rool back db
        logging.error('%s:%s: SQLite Operational Error' % (script_file,func_name))
        raise e
        return False

    except sqlite3.ProgrammingError as e:
        # connection object will rool back db
        logging.error('%s:%s: SQLite Programming Error' % (script_file,func_name))
        raise e
        return False
    
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
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