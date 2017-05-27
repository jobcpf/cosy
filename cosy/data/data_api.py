"""
Module ...

@Author: 
@Date: 

"""

################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os
import sys
import time

from datetime import datetime

import sqlite3 
#print "sqlite3 ", sqlite3.version, "run-time SQLite library version ",sqlite3.sqlite_version

# Import custom modules


################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, DB_API
global now_file
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# define working database for module
db = DB_API

# common db operations
from data_common import create_connection, insert_statement, dict_factory


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


def get_api_user(user_id = False):
    """
    Get latest user credentials or credentials of user ID for cosy API access 
    > opt userID
    < user5 {'passwd': '', 'client_secret': '', 'id': , 'client_id': '', 'user': ''}
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get user credentials' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection(db)
        # over write row_factory to return JSON
        conn.row_factory = dict_factory
        
        # cursor
        cur = conn.cursor()
        
        if user_id :
            # get entry for user ID
            cur.execute("SELECT id, user, passwd, client_id, client_secret FROM user WHERE id = ? ORDER BY create_date DESC LIMIT 1", (user_id, ))
            user5 = cur.fetchone()
        
        else:
            # get latest user entry
            cur.execute("SELECT id, user, passwd, client_id, client_secret FROM user ORDER BY create_date DESC LIMIT 1")
            user5 = cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
    
    return user5



def insert_token(user_id, json):
    """
    Insert API Token for cosy API access. (Called from api_auth.get_new_token)
    > user id, token json
    < token3 (userID, access_token, refresh_token)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert access token to db.auth' % (script_file,func_name))
    
    # define table
    table = 'auth'
    
    try :
        
        # build dynamic insert statement components
        insert3 = insert_statement(user_id, db, table, json)
        
        # connect to / create db
        conn = create_connection(db)
        
        # connection object as context manager
        with conn:
            conn.executemany("INSERT OR REPLACE INTO {tn}({tf}) VALUES ({ih})".format(tn=table,tf=insert3[0],ih=insert3[1]),insert3[2])
            
        #### Test
        #for row in conn.execute('SELECT * FROM auth ORDER BY id ASC'):
        #    print row
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        conn.close()
        
    return (user_id, json['access_token'], json['refresh_token'])

    

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
        conn = create_connection(db)
        
        if user_id :
            # cursor
            cur = conn.cursor()
            cur.execute("SELECT user_id, access_token, refresh_token FROM auth WHERE user_id = ? ORDER BY last_date DESC LIMIT 1",(user_id,))
        else:
            # cursor
            cur = conn.cursor()
            cur.execute("SELECT user_id, access_token, refresh_token FROM auth ORDER BY last_date DESC LIMIT 1")
        
        # returns (user_id, access_token, refresh_token) or None
        token3 = cur.fetchone()
        
    except Exception as e:
        raise e
    
    finally:
        conn.close()
    
    return token3



def get_api_config(user_id, table, init=None, api_id=None):
    """
    Get API configuration based on init or ID.
    # TODO: why None
    > user_id, table name, [init], [api id]
    < api5 (api_irl,cs_required,mt_required,tr_required,table_name), None
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get API token from db.auth' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection(db)
        # cursor
        cur = conn.cursor()
        
        if api_id is not None:
            cur.execute("SELECT api_url, cs_required, mt_required, tr_required, table_name FROM {tn} WHERE id = ? ORDER BY id ASC".format(tn=table),(api_id,))
        elif init is None :
            cur.execute("SELECT api_url, cs_required, mt_required, tr_required, table_name FROM {tn} ORDER BY id ASC".format(tn=table))
        elif init:
            cur.execute("SELECT api_url, cs_required, mt_required, tr_required, table_name FROM {tn} WHERE init = 1 ORDER BY id ASC".format(tn=table))
        else:
            cur.execute("SELECT api_url, cs_required, mt_required, tr_required, table_name FROM {tn} WHERE NULLIF(init,0) IS NULL ORDER BY id ASC".format(tn=table))

        # returns data or None
        api5 = cur.fetchall()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
    
    return api5
