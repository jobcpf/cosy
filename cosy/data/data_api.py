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
db = DB_API

# get database definition dict
from db_sql import DATABASES

script_file = "%s: %s" % (now_file,os.path.basename(__file__))


################## Functions ###################################### Functions ###################################### Functions ####################

def create_connection():
    """
    Create a database connection to the SQLite database specified by DB_PATH,DB_NAME
    >
    < connection object, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    #logging.debug('%s:%s: Create DB Connection' % (script_file,func_name))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,db))
        return conn
    
    except Exception as e:
        logging.error('%s:%s: Could not create connection' % (script_file,func_name))
        raise e
    
    return False



def get_api_user(user_id = False):
    """
    Get latest user credentials or credentials of user ID for cosy API access 
    > opt userID
    < user3 (userID, user, password)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get user credentials' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # cursor
        cur = conn.cursor()
        
        if user_id :
            # get entry for user ID
            cur.execute("SELECT id, user, passwd FROM user WHERE id = ? ORDER BY created_at DESC LIMIT 1", (user_id, ))
            user3 = cur.fetchone()
        
        else:
            # get latest user entry
            cur.execute("SELECT id, user, passwd FROM user ORDER BY created_at DESC LIMIT 1")
            user3 = cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
    
    return user3



def insert_token(user_id, token_json):
    """
    Insert API Token for cosy API access. (Called from api_auth.get_new_token)
    > user id, token json
    < token3 (userID, access_token, refresh_token)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert access token to db.auth' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # define table from db
        tablename = 'auth'
        
        # initial conditions
        insert_fields = ""
        insert_values = []
        
        # dynamic fields/values
        for key,val in DATABASES[db][tablename]['vfields'].iteritems() :
            insert_fields += "%s, " % key
            insert_values.append(token_json.get(key,None))
        
        # static fields/values
        insert_fields += "%s, " % 'created_at'
        insert_values.append(datetime.now())
        
        insert_fields += "%s, " % 'user_id'
        insert_values.append(user_id)
        
        # end field statement
        insert_fields = insert_fields[:-2] # loses ', ' from end of sql fields list
        
        # connection object as context manager
        with conn:
            conn.execute("INSERT INTO auth({}) VALUES (?,?,?,?,?,?,?)".format(insert_fields),insert_values)
        
        #### Test
        #for row in conn.execute('SELECT * FROM auth ORDER BY id ASC'):
        #    print row
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        return False
    
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
    return (user_id, token_json['access_token'], token_json['refresh_token'])

    

def get_api_token(user_id = False):
    """
    Get token from db.auth for cosy API access.
    > 
    < token3 (userID, access_token, refresh_token), None
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get API token from db.auth' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        if user_id :
            # cursor
            cur = conn.cursor()
            cur.execute("SELECT user_id, access_token, refresh_token FROM auth WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",(user_id,))
        else:
            # cursor
            cur = conn.cursor()
            cur.execute("SELECT user_id, access_token, refresh_token FROM auth ORDER BY created_at DESC LIMIT 1")
        
        # returns (user_id, access_token, refresh_token) or None
        token3 = cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
    
    return token3



def insert_api_config(user_id, json):
    """
    Insert or Replace API configuration cosy API access.
    returns True on create
    > user ID, json
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert or Replace API configuration to db.apiaccessconfig' % (script_file,func_name))
    
    table = 'apiaccessconfig'
    
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
        insert_fields += "%s, " % 'created_at'
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
            
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn} ORDER BY id'.format(tn=table)):
        #    print row
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        return False

    except sqlite3.OperationalError as e:
        # connection object will rool back db
        logging.error('%s:%s: SQLite Operational Error' % (script_file,func_name))
        raise e
        #return False

    except sqlite3.ProgrammingError as e:
        # connection object will rool back db
        logging.error('%s:%s: SQLite Programming Error' % (script_file,func_name))
        raise e
        #return False
    
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
    return True
