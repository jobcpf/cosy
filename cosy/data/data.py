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
        #raise e
        return False # returns false if no control unit discovered...

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


def manage_control(user_id, table, sysID, status = None):
    """
    Enforce 'self' bool for control unit
    > user_id, table, sysID, [status]
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
                    conn.execute("UPDATE {tn} SET status_bool = 1, status = ? WHERE sysID = ?;".format(tn=table),(status,sysID))
                else:
                    conn.execute("UPDATE {tn} SET status_bool = 0, status = ? WHERE sysID = ?;".format(tn=table),(status,sysID))
                
            else:
                # enforce cuID
                conn.execute("UPDATE {tn} SET self_bool = 0;".format(tn=table))
                conn.execute("UPDATE {tn} SET self_bool = 1 WHERE sysID = ?;".format(tn=table),(sysID,))

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
    logging.debug('%s:%s: Get active control unit and associated user id from table: %s' % (script_file,func_name,table))

    try :
        
        # connect to / create db
        conn = create_connection(db)
        cur = conn.cursor()
        
        # get data
        cur.execute("SELECT user_id, sysID, system_type from {tn} WHERE self_bool = 1;".format(tn=table))
        id3 = cur.fetchone()
            
    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        #raise e
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    finally:
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
            
        conn.close()
        
    return id3


def manage_comms(id3, sent_conf = False):
    """
    Get comms for target system
    > id3 (userID,sysID,system_type), [API sent confirmation transactionID list]
    < True, False
    
    TODO - currently one way - need both ways
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage communications and events.' % (script_file,func_name))

    try :
        # connect to / create db
        conn = create_connection(db)
        
####### Update comms queue and events to confirm sent
        if sent_conf :
            # iterate transactions and update sent in comms queue and event TODO: update many without iterator
            with conn:
                for idents in sent_conf:
                    conn.execute("UPDATE {tn} SET comm_sent = 1 WHERE control_sys = ? AND transactionID = ?;".format(tn=TB_COMM),idents)
                    conn.execute("UPDATE {tn} SET link_confirmed = 1 WHERE control_sys = ? AND transactionID = ?;".format(tn=TB_CEVENT),idents)
            
            # return true
            ret_val = True
            
####### Sync events and comms queue
        else :
            
            with conn :
            
            ### NEW COMMS QUEUE >> EVENTS
            
                #get incomplete items from comms queue & insert into events where targeted
                conn.execute("""INSERT INTO {tu} (control_sys, source, target, data, transactionID, priority, last_date, user_id)
                                    SELECT control_sys, source, target, data, transactionID, priority, last_date, user_id
                                    FROM {tn}
                                    WHERE control_sys = ?
                                    AND target = ?
                                    AND NOT EXISTS (
                                        SELECT a.*
                                        FROM {tn} AS a
                                        INNER JOIN {tu} AS b ON a.transactionID = b.transactionID AND a.control_sys = b.control_sys
                                    );""".format(tn=TB_COMM,tu=TB_CEVENT),(id3[1], id3[2]))
            
            
            ### NEW EVENTS >> COMMS QUEUE
                
                # generate transactionID in events TODO: test consistency of transactionID generated here and in Django
                # alternative: event['transactionID'] = "3%s%s%s" % (str(event['source']).zfill(2),str(event['event_type']).zfill(2),event['id'])
                conn.execute("""UPDATE {tn}
                             SET transactionID = '3'||substr('00'||source,-2,2)||(SELECT substr('00'||event_type,-2,2) FROM {tn2} WHERE {tn}.event_config = {tn2}.id)||id
                             WHERE target NOT NULL
                             AND transactionID IS NULL
                             ;""".format(tn=TB_CEVENT,tn2=TB_CECONF))
                
                # get incomplete items from events & insert into comms queue where targeted
                conn.execute("""INSERT INTO {tu} (control_sys, transactionID, source, target, data, priority, last_date, user_id, complete_req)
                                    SELECT control_sys, transactionID, source, target, data, priority, last_date, user_id, link_complete_req
                                    FROM {tn} AS a
                                    WHERE control_sys = ?
                                    AND source = ?
                                    AND complete = 0
                                    AND link_confirmed = 0
                                    AND target IS NOT NULL
                                    AND transactionID IS NOT NULL
                                    AND NOT EXISTS (
                                        SELECT *
                                        FROM {tn} AS b
                                        INNER JOIN {tu} AS c ON b.control_sys = c.control_sys AND b.transactionID = c.transactionID
                                        WHERE a.transactionID = b.transactionID
                                    )
                                    ;""".format(tn=TB_CEVENT,tu=TB_COMM),(id3[1], id3[2]))
            
            ## over write row_factory to return JSON
            #conn.row_factory = dict_factory
            #cur = conn.cursor()
            #
            ## get data
            #cur.execute("""SELECT a.source, b.event_type, a.id, a.target, a.data, a.priority, a.link_complete_req, a.control_sys
            #               FROM {tn} AS a
            #               INNER JOIN {tn2} AS b ON a.event_config = b.id
            #               WHERE target IS NOT NULL
            #               AND transactionID IS NULL
            #               AND complete = 0
            #               AND link_confirmed = 0
            #               AND control_sys = ?
            #               AND source = ?
            #               ORDER BY priority DESC;
            #            """.format(tn=TB_CEVENT,tn2=TB_CECONF),(id3[1],id3[2]))
            #
            #event_list = cur.fetchall()
            #
            #for event in event_list:
            #    # generate transactionID - save to events & comms
            #    event['transactionID'] = "3%s%s%s" % (str(event['source']).zfill(2),str(event['event_type']).zfill(2),event['id'])
            #    event['user_id'] = id3[0]
            #    event['last_date'] = datetime.now()
            #    
            #    # insert events to comms queue where transactionID not already present
            #    with conn:
            #        conn.execute("""INSERT OR IGNORE INTO {tn}(
            #                        control_sys, source, target, complete_req, data, transactionID, user_id, last_date
            #                        ) VALUES (
            #                        ?, ?, ?, ?, ?, ?, ?, ?
            #                        );""".format(tn=TB_COMM),(
            #                        event['control_sys'],
            #                        event['source'],
            #                        event['target'],
            #                        event['link_complete_req'],
            #                        event['data'],
            #                        event['transactionID'],
            #                        event['user_id'],
            #                        event['last_date']
            #                        ))
            #        
            #        # update event with transactionID
            #        conn.execute("UPDATE {tn} SET transactionID = ? WHERE id = ?;".format(tn=TB_CEVENT),(event['transactionID'],event['id']))
                        
            ### UPDATE EVENTS >> COMMS QUEUE
            
            # update comms queue where events completed
                conn.execute("""UPDATE {tu}
                                SET data = (SELECT data FROM {ts}
                                            WHERE {ts}.control_sys = {tu}.control_sys
                                            AND {ts}.transactionID = {tu}.transactionID
                                            ), 
                                    complete = 1
                                WHERE
                                    EXISTS (
                                        SELECT * FROM {ts}
                                        WHERE {ts}.control_sys = {tu}.control_sys
                                        AND {ts}.transactionID = {tu}.transactionID
                                        AND {ts}.complete = 1 
                                        AND {tu}.complete = 0
                                    );
                            """.format(tu=TB_COMM, ts=TB_CEVENT))
            
            ### UPDATE COMMS QUEUE >> EVENTS
            
            # update comms queue where events completed
                conn.execute("""UPDATE {tu}
                                SET data = (SELECT data FROM {ts}
                                            WHERE {ts}.control_sys = {tu}.control_sys
                                            AND {ts}.transactionID = {tu}.transactionID
                                            ), 
                                    complete = 1
                                WHERE
                                    EXISTS (
                                        SELECT * FROM {ts}
                                        WHERE {ts}.control_sys = {tu}.control_sys
                                        AND {ts}.transactionID = {tu}.transactionID
                                        AND {ts}.complete = 1 
                                        AND {tu}.complete = 0
                                    );
                            """.format(tu=TB_CEVENT, ts=TB_COMM))
            
########### Return JSON comms queue for API UPDATE and POST

            # over write row_factory to return JSON
            conn.row_factory = dict_factory
            cur = conn.cursor()

            ### get JSON comms events that need API POST
            
            # define fields for select
            fields = "control_sys, meter, data, transactionID, source, target, priority, complete_req, complete"
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE complete = 1
                        AND source = ?
                        AND comm_sent = 0
                        ORDER BY priority DESC;
                        """.format(tn=TB_COMM,tf=fields),(id3[2],))
            
            api_post = cur.fetchall()
            
            ### get JSON comms events that need API PUT (UPDATES)
            
            # define fields for select
            #fields = "sysID, meter, data, transactionID, source, target, priority, complete_req, complete, URI"
            fields = "control_sys, transactionID, data, complete, URI"
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE complete = 1
                        AND source != ?
                        AND comm_sent = 0
                        AND complete_req = 1
                        ORDER BY priority DESC;
                        """.format(tn=TB_COMM,tf=fields),(id3[2],))
            
            api_put = cur.fetchall()
            
            # return pu and post JSON
            ret_val = (api_put,api_post)
            
            
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



