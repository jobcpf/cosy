"""
Module to initiate data structures.

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
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# define working database for module
db = DB_API

# common db operations
from data_common import create_connection, execute_sql

################## Functions ###################################### Functions ###################################### Functions ####################

def init_db(databases):
    """
    Create databases for COSY.
    > databases[list of db dict definitions]
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate databases' % (script_file,func_name))
    
    # iterate databases & build
    for db, db_sql_dict in databases.iteritems() :
        
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
                for vfield, detail in db_sql_dict[table]['vfields'].iteritems():
                    sql_str += "%s %s, " % (vfield, detail)
            
            if 'sfields' in db_sql_dict[table] :
                for sfield, detail in db_sql_dict[table]['sfields'].iteritems():
                    sql_str += "%s %s, " % (sfield, detail)
            
            if 'constraints' in db_sql_dict[table] :
                for cfield, detail in db_sql_dict[table]['constraints'].iteritems():
                    sql_str += "%s %s, " % (cfield, detail)
                    
            # terminate sql statement
            sql_str = sql_str[:-2]
            sql_str += ");"
            
            # create table
            execute_sql(db, sql_str)
            
            if 'commands' in db_sql_dict[table] :
                for command, detail in db_sql_dict[table]['commands'].iteritems():
                    sql_str = "%s %s;" % (command, detail)
            
                    # create table
                    execute_sql(db, sql_str)
            
    return True


def init_user(table,auth_json):
    """
    Create initial user credentials for cosy API access.
    TODO: Access user:password from secure file via ssh...
    > table, json auth details
    < user5 {'passwd': '', 'client_secret': '', 'id': , 'client_id': '', 'user': ''}
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Create initial user credentials in table: %s' % (script_file,func_name,table))
    
    try :
        # connect to / create db
        conn = create_connection(db)
        
        # generate values to insert
        user_detail = (auth_json['user'],
                       auth_json['user'],
                       auth_json['passwd'],
                       auth_json['client_id'],
                       auth_json['client_secret'],
                       datetime.now())
        
        # connection object as context manager
        with conn:
            cur = conn.cursor()
            cur.execute("""INSERT OR REPLACE INTO {tn}(id, user, passwd, client_id, client_secret, create_date) VALUES (
                        (SELECT id FROM {tn} WHERE user = ?), ?, ?, ?, ?, ?
                        )""".format(tn=table),user_detail)
            
            # get userID to return
            userID = cur.lastrowid
            
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: Table does not exist - database file missing?' % (script_file,func_name))
        raise e
    
    finally:
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
        
        conn.close()
    
    # add user id to auth_json > user5
    auth_json['id'] = userID
        
    return auth_json
