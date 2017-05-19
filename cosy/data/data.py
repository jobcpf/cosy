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
    
    # connection object using 'with' will rool back db on exception and close on complete
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQL IntegrityError: %s' % (script_file,func_name,e))
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

    # connection object using 'with' will rool back db on exception and close on complete
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQL IntegrityError: %s' % (script_file,func_name,e))
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
    < id3 (userID,cuID,sysID)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get active control unit and assicuated user id from table: %s' % (script_file,func_name,table))

    try :
        
        # connect to / create db
        conn = create_connection(db)
        cur = conn.cursor()
        
        # get data
        cur.execute("SELECT user_id, cuID, system_type from {tn} WHERE self = 1;".format(tn=table))
        id3 = cur.fetchone()
            
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        #raise e
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
            
        conn.close()
        
    return id3


def manage_comms(id3, sent_conf = False):
    """
    Get comms for target system
    > id3 (userID,cuID,sysID), [API sent confirmation transactionID list]
    < True, False
    
    TODO - currently one way - need both ways
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage communications and events.' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection(db)
        
        ## confirm events sent to API
        if sent_conf :
            
            # iterate transactions and update sent
            for transactionID in sent_conf:
                conn.execute("UPDATE {tn} SET comm_sent = 1 WHERE transactionID = ?;".format(tn=TB_COMM),(transactionID,))
                
                ret_val = True
            
        ## sync events and queue - return API update events
        else :
            
            ### get incomplete data from comms queue
            
            # define fields for select / insert
            fields = "control_unit, source, target, data, transactionID, priority, last_date, user_id"
            
            cur = conn.cursor()
            
            # get data
            cur.execute("""SELECT {tf} FROM {tn} WHERE control_unit = ? AND target = ? AND comm_complete = 0;
                        """.format(tn=TB_COMM,tf=fields),(id3[1], id3[2]))
            comms_list = cur.fetchall()
            
            ### insert comms data data to events list where transactionID not already present
            
            # build fields holder based on values in fields
            fields_holder = "?, " * len(comms_list[0])
            fields_holder = fields_holder[:-2] # loses ', ' from end of holder list
            
            # connection object as context manager
            with conn:
                conn.executemany("""INSERT OR IGNORE INTO {tn}({tf}) VALUES ({ih})""".format(tn=TB_CEVENT,tf=fields,ih=fields_holder),comms_list)
            
            ## update where events completed
                conn.execute("""UPDATE {tu}
                                SET
                                    data = (SELECT data FROM {ts} WHERE {ts}.transactionID = {tu}.transactionID), 
                                    comm_complete = 1
                                WHERE
                                    EXISTS (
                                        SELECT * FROM {ts}
                                        WHERE {ts}.transactionID = {tu}.transactionID
                                        AND {ts}.complete = 1 
                                        AND {tu}.comm_complete = 0
                                    );
                            """.format(tu=TB_COMM, ts=TB_CEVENT))
            
            
            ## get JSON comms events that need API updates
            
            # define fields for select / insert
            #fields = "control_unit, meter, data, transactionID, source, target, priority, comm_complete_req, comm_complete, URI"
            fields = "data, comm_complete, URI"
            
            # over write row_factory to return JSON
            conn.row_factory = dict_factory
            cur = conn.cursor()
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE comm_complete = 1
                        AND comm_sent IS NULL
                        AND comm_complete_req = 1;
                        """.format(tn=TB_COMM,tf=fields))
            
            ret_val = cur.fetchall()
            
            
    # connection object using 'with' will rool back db on exception and close on complete
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQL IntegrityError: %s' % (script_file,func_name,e))
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
    
    except ValueError as e:
        logging.error('%s:%s: ValueError: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    #except Exception as e:
    #    # connection object will rool back db
    #    raise e
    
    finally:
        
        #### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_CEVENT)):
        #    print row
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_COMM)):
        #    print row
            
        conn.close()
        
    return ret_val



