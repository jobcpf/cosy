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

# define working database for module
db = DB_DATA

# get database definition dict
from db_sql import DATABASES

from data_common import create_connection, insert_statement

################## Functions ###################################### Functions ###################################### Functions ####################

def insert_data(user_id, table, json):
    """
    Insert or Replace data for database.
    > user_id, table name, json data
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert or Replace data to table: %s.%s' % (script_file,func_name,db,table))
    
    conn = create_connection(db)
    
    try :
        
        # build dynamic insert statement components
        insert3 = insert_statement(user_id, db, table, json)
        
        # connect to / create db
        conn = create_connection(db)
        
        #print insert3[0]
        #print insert3[1]
        #print insert3[2]
        
        # connection object as context manager
        with conn:
            conn.executemany("INSERT OR REPLACE INTO {tn}({tf}) VALUES ({ih})".format(tn=table,tf=insert3[0],ih=insert3[1]),insert3[2])
    
    # connection object using 'with' will rool back db on exception
    except sqlite3.IntegrityError:
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        raise e
        return False

    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error' % (script_file,func_name))
        raise e
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error' % (script_file,func_name))
        raise e
        return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
        
        conn.close()
        
    return True


def manage_control(user_id, table, cuID, status = None):
    """
    Enforce 'self' bool for control unit
    > user_id, table, cuID
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage control unit details in table: %s' % (script_file,func_name,table))

    try :
        
        # connect to / create db
        conn = create_connection(db)
        
        # connection object as context manager
        with conn:
            
            if status is not None :
                # status update
                if status == 'OK':
                    conn.execute("UPDATE {tn} SET status_bool = 1, status = ? WHERE cuID = ?;".format(tn=table),(status,cuID))
                else:
                    conn.execute("UPDATE {tn} SET status_bool = 0, status = ? WHERE cuID = ?;".format(tn=table),(status,cuID))
                
            else:
                # enforce cuID
                conn.execute("UPDATE {tn} SET self = 0;".format(tn=table))
                conn.execute("UPDATE {tn} SET self = 1 WHERE cuID = ?;".format(tn=table),(cuID,))

    # connection object using 'with' will rool back db on exception
    except sqlite3.IntegrityError:
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        raise e
        return False

    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error' % (script_file,func_name))
        raise e
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error' % (script_file,func_name))
        raise e
        return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
            
        conn.close()
        
    return True


def get_control(table):
    """
    Get control unit and associated userID
    > 
    < id2 (user ID, cuID)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get active control unit and assicuated user id from table: %s' % (script_file,func_name,table))

    try :
        
        # connect to / create db
        conn = create_connection(db)
        cur = conn.cursor()
        
        # get data
        cur.execute("SELECT user_id, cuID from {tn} WHERE self = 1;".format(tn=table))
        id2 = cur.fetchone()
            
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file, func_name, e))
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error' % (script_file,func_name))
        raise e
        return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
            
        conn.close()
        
    return id2


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