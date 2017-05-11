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


################## DB Structure #################################### DB Structure #################################### DB Structure ##################

db_api_sql = [
        """CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            user TEXT unique NOT NULL,
            passwd TEXT NOT NULL,
            control_unit INTEGER,
            created_at TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS auth (
            id INTEGER PRIMARY KEY,
            access_token TEXT NOT NULL,
            token_type TEXT NOT NULL,
            expires_in INTEGER,
            refresh_token TEXT,
            scope TEXT,
            created_at TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );""",
]


################## Functions ###################################### Functions ###################################### Functions ####################


# create database connection
def create_connection():
    """
    Create a database connection to the SQLite database specified by DB_PATH,DB_API
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    logging.debug('%s:%s: Create DB Connection' % (script_file,func_name))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,DB_API))
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
        
        # iterate db_api_sql and create tables
        for create_table_sql in db_api_sql :
        
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


def init_user():
    """
    Create initial user credentials for cosy API access.
    TODO: Access user:password from secure file via ssh...
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial user credentials' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        ### temp
        user = 'apitest'
        passwd = 'buggeryouall'
        
        # generate values to insert
        user_detail = (user,passwd,datetime.now())
        
        # connection object as context manager
        with conn:
            conn.execute('INSERT INTO user(user,passwd,created_at) VALUES (?,?,?)',user_detail)
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: user already exists: %s' % (script_file,func_name,user))
        
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()


def insert_token(user_id, token_json):
    """
    Insert API Token for cosy API access.
        
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial user credentials' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # extract values from JSON etc.
        #user_id = user_id
        access_token = token_json['access_token']
        token_type = token_json['token_type']
        expires_in = token_json['expires_in']
        refresh_token = token_json['refresh_token']
        scope = token_json['scope']
        created_at = datetime.now()
        
        # generate values to insert
        token_detail = (user_id, access_token, token_type, expires_in, refresh_token, scope, created_at)
        
        # connection object as context manager
        with conn:
            conn.execute('INSERT INTO auth(user_id, access_token, token_type, expires_in, refresh_token, scope, created_at) VALUES (?,?,?,?,?,?,?)',token_detail)
        
    except sqlite3.IntegrityError:
        # connection object will rool back db
        logging.error('%s:%s: item already exists' % (script_file,func_name))
        
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
    return True

    
def get_api_user():
    """
    Get user credentials for cosy API access.
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get user credentials' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # cursor
        cur = conn.cursor()
        cur.execute("SELECT id, user, passwd FROM user ORDER BY created_at DESC")
        
        return cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()


def get_api_token():
    """
    Get token from db.auth for cosy API access.
    returns ('access_token','refresh_token')
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get API token from db' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # cursor
        cur = conn.cursor()
        cur.execute("SELECT access_token, refresh_token  FROM auth ORDER BY created_at DESC")
        
        return cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
