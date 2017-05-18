"""
Module to initiate data structures.

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
db = DB_API

# common db operations
from data_common import create_connection

################## Functions ###################################### Functions ###################################### Functions ####################

def create_table(conn, create_table_sql) :
    """
    Create a table from the create_table_sql statement
    >
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    try:
        with conn:
            conn.execute(create_table_sql)
    
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error' % (script_file,func_name))
        raise e
    
    except Exception as e:
        logging.error('%s:%s: Could not create table' % (script_file,func_name))
        raise e
    
    return True


def init_db(databases):
    """
    Create databases for COSY.
    > databases[list of db dict definitions]
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate databases' % (script_file,func_name))
    
    for db, db_sql_dict in databases.iteritems() :
        
        # connect to / create db
        conn = create_connection(db)
        
        # if connection possible
        if conn is not None:
            
            # get execute order list from 'sort' value
            exec_order = sorted(db_sql_dict, key=lambda x: db_sql_dict[x]['sort'])
            
            # Get sorted order table build data
            for table in exec_order:
                
                # initiate CREATE TABLE sql
                sql_str = "" + "CREATE TABLE IF NOT EXISTS %s (" % table
                
                if 'pk' in db_sql_dict[table] :
                    for pk, detail in db_sql_dict[table]['pk'].iteritems():
                        sql_str = sql_str + "%s %s, " % (pk, detail)
                
                if 'vfields' in db_sql_dict[table] :
                    for field, detail in db_sql_dict[table]['vfields'].iteritems():
                        sql_str += "%s %s ," % (field, detail)
                
                if 'sfields' in db_sql_dict[table] :
                    for field, detail in db_sql_dict[table]['sfields'].iteritems():
                        sql_str += "%s %s, " % (field, detail)
                
                if 'constraints' in db_sql_dict[table] :
                    for constraint, detail in db_sql_dict[table]['constraints'].iteritems():
                        sql_str += "%s %s ," % (constraint, detail)
                
                # terminate sql statement
                sql_str = sql_str[:-2]
                sql_str += ");"
                
                # create table
                create_table(conn, sql_str)
        
            # Committing changes and closing the connection to the database file
            conn.commit()
            conn.close()
            
        else:
            logging.error('%s:%s: Cannot create database connection.' % (script_file,func_name))
            return False

    return True


def init_user(table,user,passwd):
    """
    Create initial user credentials for cosy API access.
    TODO: Access user:password from secure file via ssh...
    > 
    < user3 (userID, user, password)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial user credentials in table: %s' % (script_file,func_name,table))
    
    try :
        # connect to / create db
        conn = create_connection(db)
        
        # generate values to insert
        user_detail = (user,passwd,datetime.now())
        
        # connection object as context manager
        with conn:
            cur = conn.cursor()
            cur.execute('INSERT OR REPLACE INTO {tn}(user, passwd, create_date) VALUES (?,?,?)'.format(tn=table),user_detail)
            
            # get userID to return
            userID = cur.lastrowid
            
        #### Test
        #for row in conn.execute('SELECT * FROM user ORDER BY id'):
        #    print row
    
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: Table does not exist - database file missing?' % (script_file,func_name))
        raise e
        
    except Exception as e:
        # connection object will rool back db
        raise e
    
    finally:
        conn.close()
        
    return (userID,user,passwd)
