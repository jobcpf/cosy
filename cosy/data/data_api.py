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

# set database
DB_NAME = DB_API

# set database sql dictionary
from db_sql import db_api_dict
db_sql_dict = db_api_dict

################## Functions ###################################### Functions ###################################### Functions ####################


def create_connection():
    """
    Create a database connection to the SQLite database specified by DB_PATH,DB_NAME
    returns connection to db
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    logging.debug('%s:%s: Create DB Connection' % (script_file,func_name))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,DB_NAME))
        return conn
    
    except Exception as e:
        logging.error('%s:%s: Could not create connection' % (script_file,func_name))
        raise e
    
    return None


def create_table(conn, create_table_sql) :
    """
    Create a table from the create_table_sql statement
    returns True on creation
    
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
    returns true on creation
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial database' % (script_file,func_name))
    
    # connect to / create db
    conn = create_connection()
    
    # if connection possible
    if conn is not None:
        
        # get execute order list from 'sort' value
        exec_order = sorted(db_api_dict, key=lambda x: db_api_dict[x]['sort'])
        
        # Get sorted order table build data
        for table in exec_order:
            
            # initiate CREATE TABLE sql
            sql_str = "" + "CREATE TABLE IF NOT EXISTS %s (" % table
            
            for pk, detail in db_api_dict[table]['pk'].iteritems():
                sql_str = sql_str + "%s %s" % (pk, detail)
            
            if 'apifields' in db_api_dict[table] :
                for field, detail in db_api_dict[table]['apifields'].iteritems():
                    sql_str += ", %s %s" % (field, detail)
            
            if 'appendfields' in db_api_dict[table] :
                for field, detail in db_api_dict[table]['appendfields'].iteritems():
                    sql_str += ", %s %s" % (field, detail)
            
            if 'contraints' in db_api_dict[table] :
                for constraint, detail in db_api_dict[table]['contraints'].iteritems():
                    sql_str += ", %s %s" % (constraint, detail)
            
            # terminate sql statement
            sql_str += ");"
            
            # create table
            create_table(conn, sql_str)
    
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
    returns (userID,user,password)
    
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
            cur = conn.cursor()
            cur.execute('INSERT OR REPLACE INTO user(user, passwd, created_at) VALUES (?,?,?)',user_detail)
            
            # get userID toreturn
            userID = cur.lastrowid
            
        #### Test
        #for row in conn.execute('SELECT * FROM user ORDER BY id'):
        #    print row
            
    except sqlite3.IntegrityError: # TODO: uneccesary as INSERT OR REPLACE should prevent sqlite3.IntegrityError
        # connection object will roll back db
        logging.error('%s:%s: user already exists: %s' % (script_file,func_name,user))
        
        cur.execute("SELECT id, user, passwd FROM user WHERE user = ?", (user,))
        return cur.fetchone()
        
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
    return (userID,user,passwd)


def insert_token(user_id, token_json):
    """
    Insert API Token for cosy API access.
    returns token3 (userID, access_token, refresh_token)
    
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
        for key,val in db_sql_dict[tablename]['apifields'].iteritems() :
            insert_fields += "%s, " % key
            insert_values.append(token_json[key])
        
        # static fields/values
        insert_fields += "%s, " % 'created_at'
        insert_values.append(datetime.now())
        
        insert_fields += "%s, " % 'user_id'
        insert_values.append(user_id)
        
        # end field statement
        insert_fields = insert_fields[:-2]
        
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


def get_api_user():
    """
    Get user credentials for cosy API access.
    returns (userID,user,password)
    
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
    returns token3 (userID, access_token, refresh_token)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get API token from db.auth' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        # cursor
        cur = conn.cursor()
        cur.execute("SELECT user_id, access_token, refresh_token FROM auth ORDER BY created_at DESC")
        
        token3 = cur.fetchone()
        
    except Exception as e:
        # Roll back any change if something goes wrong
        raise e
    
    finally:
        conn.close()
    
    return token3


def insert_api_config(user_id, api_json_all):
    """
    Insert or Replace API configuration cosy API access.
    returns True on create
        
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Insert or Replace API configuration to db.apiaccessconfig' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection()
        
        api_detail = []
        
        for api_json in api_json_all:
            
            # extract values from JSON etc.
            #user_id = user_id
            apiid = api_json['id']
            api_url = api_json['api_url']
            api_version = api_json['api_version']
            refresh = api_json['refresh']
            init = api_json['init']
            cs_required = api_json['cs_required']
            tr_required = api_json['tr_required']
            mt_required = api_json['mt_required']
            created_at = datetime.now()
            
            # generate values to insert
            api_row = (apiid, user_id, api_url, api_version, refresh, init, cs_required, tr_required, mt_required, created_at)
            
            api_detail.append(api_row)
        
        # connection object as context manager
        with conn:
            conn.executemany('INSERT OR REPLACE INTO apiaccessconfig(apiid, user_id, api_url, api_version, refresh, init, cs_required, tr_required, mt_required, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)',api_detail)
        
        #### Test
        #for row in conn.execute('SELECT * FROM apiaccessconfig ORDER BY apiid'):
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
        
    return True
