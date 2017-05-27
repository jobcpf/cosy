"""
Module: Common operations for databases

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

import os
import sys
import time

from datetime import datetime

import sqlite3 
#print "sqlite3 ", sqlite3.version, "run-time SQLite library version ",sqlite3.sqlite_version

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, DB_PATH
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# get database definition dict
from db_sql import DATABASES

################## Functions ###################################### Functions ###################################### Functions ####################

def create_connection(db):
    """
    Create a database connection to the SQLite database specified by DB_PATH,db
    >
    < connection object, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    #logging.debug('%s:%s: Create DB Connection for database %s' % (script_file,func_name,db))
    
    try:
        # connect to DB
        conn = sqlite3.connect('%s/%s' % (DB_PATH,db))
        return conn
    
    except Exception as e:
        logging.error('%s:%s: Could not create connection' % (script_file,func_name))
        raise e
    
    return False



def execute_sql(db, sql) :
    """
    Execute SQL statement on database.
    > database, sql statement
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    # connect to / create db
    conn = create_connection(db)
    
    try:
        with conn:
            conn.execute(sql)
    
    # connection object using 'with' will roll back db on exception & close connection when complete
    
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQLite item already exists: %s' % (script_file,func_name,e))
        raise e
        #return False

    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        raise e
        #return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    #except Exception as e:
    #    raise e
    
    return True



def dict_factory(cursor, row):
    """
    SQLite Cursor method for returning JSON.
    
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



def insert_statement(user_id, db, table, json_list):
    """
    Build sql inserts for dynamic data insert
    > user_id, table name, json data
    < (insert_fields,insert_holder,insert_val_list)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    #logging.debug('%s:%s: Build data insert statement for table: %s.%s' % (script_file,func_name,db,table))
    
    try: 
        # initial conditions
        insert_val_list = []
        
        ## build field list
        
        # initial conditions
        insert_fields = ""
        
        if DATABASES[db][table]['vfields']:
            # dynamic fields/values
            for key,val in DATABASES[db][table]['vfields'].iteritems() :
                insert_fields += "%s, " % key
        
        # static fields/values
        insert_fields += "%s, " % 'last_date'
        insert_fields += "%s, " % 'user_id'
        
        # end field statement
        insert_fields = insert_fields[:-2] # loses ', ' from end of sql fields list
        
        # check if single json returned or list - convert to list for iter
        if not isinstance(json_list,list):
            json_list = [json_list]
            
        ## build insert values from json list
        for individual_json in json_list:
            
            # initial conditions
            insert_values = []
            
            if DATABASES[db][table]['vfields']:
                # dynamic fields/values
                for key,val in DATABASES[db][table]['vfields'].iteritems() :
                    insert_values.append(individual_json.get(key,None))
            
            # static fields/values
            insert_values.append(datetime.now())
            insert_values.append(user_id)
            
            # stack to detail list
            insert_val_list.append(tuple(insert_values))
            
        # build insert holder based on values
        insert_holder = "?, " * len(insert_values)
        insert_holder = insert_holder[:-2] # loses ', ' from end of holder list
        
        return (insert_fields,insert_holder,insert_val_list)
        
    except Exception as e:
        logging.error('%s:%s: Error generating insert statement: %s' % (script_file,func_name,e))
        raise e
    
    return False