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

from global_config import logging, now_file, DB_DATA, TB_COMM, TB_CEVENT, TB_CECONF
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
    N.B. Causes id to increment if inserting without id and will reset defaults where fields not passed.
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
        return False # e.g. returns false if no control unit discovered...

    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        raise e
        #return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    finally:
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
        conn.close()
        
    return True


def manage_control(table, sysID = None, method = None, data = None):
    """
    Enforce 'self' bool for control unit
    > user_id, table, sysID, [status]
    < idst, False
    idst:{'status': u'OK',
          'user_id': 1,
          'status_bool': 1,
          'URI': u'http://172.16.32.40:8000/api/0.1/env/reg/710011/',
          'sysID': 710011,
          'system_type': 31,
          'last_config: [date],}
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage control unit method: %s' % (script_file,func_name,method))

    try :
        
        # connect to / create db
        conn = create_connection(db)
        
        # connection object as context manager
        with conn:
            
            if method == 'status':
                # status update
                if data is None:
                    conn.execute("UPDATE {tn} SET status_bool = 1, status = 'OK' WHERE sysID = ?;".format(tn=table),(sysID,))
                else:
                    conn.execute("UPDATE {tn} SET status_bool = 0, status = ? WHERE sysID = ?;".format(tn=table),(data,sysID))
            elif method == 'config':
                conn.execute("UPDATE {tn} SET last_config = ? WHERE sysID = ?;".format(tn=table),(datetime.now(),sysID))
            elif method == 'self':
                # enforce cuID
                conn.execute("UPDATE {tn} SET self_bool = 0;".format(tn=table))
                conn.execute("UPDATE {tn} SET self_bool = 1 WHERE sysID = ?;".format(tn=table),(sysID,))
        
            ###### Test
            #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
            #    print row
            
            ## get idst to return
            
            # over write row_factory to return JSON
            conn.row_factory = dict_factory
            cur = conn.cursor()
        
            # get data
            cur.execute("SELECT user_id, sysID, system_type, status_bool, status, URI, last_config from {tn} WHERE self_bool = 1;".format(tn=table))
            idst = cur.fetchone()
        
    # connection object using 'with' will rool back db on exception and close on complete
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQL IntegrityError: %s' % (script_file,func_name,e))
        raise e
        #return False

    except sqlite3.OperationalError as e:
        logging.error('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        #raise e
        return False

    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    finally:
        conn.close()
        
    return idst


#def get_control(table):
#    """
#    Get control unit and associated userID
#    > table
#    < idst, False
#    idst:{'status': u'OK',
#          'user_id': 1,
#          'status_bool': 1,
#          'URI': u'http://172.16.32.40:8000/api/0.1/env/reg/710011/',
#          'sysID': 710011,
#          'system_type': 31,
#          'last_config: [date],}
#    
#    """
#    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
#    logging.debug('%s:%s: Get active control unit and associated user id from table: %s' % (script_file,func_name,table))
#
#    try :
#        # connect to / create db
#        conn = create_connection(db)
#        
#        # over write row_factory to return JSON
#        conn.row_factory = dict_factory
#        
#        cur = conn.cursor()
#        
#        # get data
#        cur.execute("SELECT user_id, sysID, system_type, status_bool, status, URI, last_config from {tn} WHERE self_bool = 1;".format(tn=table))
#        idst = cur.fetchone()
#            
#    except sqlite3.OperationalError as e:
#        logging.debug('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
#        #raise e
#        return False
#
#    except sqlite3.ProgrammingError as e:
#        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
#        raise e
#        #return False
#    
#    finally:
#        ##### Test
#        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
#        #    print row
#            
#        conn.close()
#        
#    return idst


def manage_comms(idst, data_json = False, method = None):
    """
    Get comms for target system
    > idst, [API sent confirmation transactionID list]
    < True, (api_put, api_post, api_get)
    
    TODO - currently one way - need both ways
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage communications data method %s' % (script_file,func_name,method))

    try :
        # connect to / create db
        conn = create_connection(db)
        
####### Update comms queue from API call
        if method == 'insert' :
            
            with conn:
                for json in data_json :
                    conn.execute("""INSERT OR REPLACE INTO {tn} (id, comm_sent, control_sys, transactionID, source, target, data, priority, URI, complete_req, complete, last_date, user_id)
                                    VALUES (
                                    (SELECT id FROM {tn} WHERE control_sys = {cs} AND transactionID = {ti}),
                                    ifnull((SELECT comm_sent FROM {tn} WHERE control_sys = {cs} AND transactionID = {ti}),0),
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                """.format(tn=TB_COMM,cs=json['control_sys'],ti=json['transactionID']),(
                                json['control_sys'],
                                json['transactionID'],
                                json.get('source',None),
                                json.get('target',None),
                                json.get('data',None),
                                json.get('priority',None),
                                json.get('URI',None),
                                json.get('complete_req',0),
                                json.get('complete',0),
                                datetime.now(),
                                idst['user_id']
                                ))
            # return true
            ret_val = True
        
####### Update comms queue and events
        elif method == 'updatelist' :
            # iterate transactions and update sent in comms queue and event TODO: update many without iterator
            with conn:
                for ident in data_json:
                    conn.execute("UPDATE {tn} SET comm_sent = 1, URI=?, complete = ? WHERE control_sys = ? AND transactionID = ?;".format(tn=TB_COMM),ident)
                    # remove URI
                    ident = ident[1:]
                    conn.execute("UPDATE {tn} SET link_confirmed = 1, complete = ? WHERE control_sys = ? AND transactionID = ?;".format(tn=TB_CEVENT),ident)
            
            # return true
            ret_val = True
            
####### Sync events and comms queue
        else :
            with conn :
            
            ### NEW COMMS QUEUE >> EVENTS
            
                # get incomplete items from comms queue & insert into events where targeted
                conn.execute("""INSERT INTO {tu} (control_sys, source, target, data, transactionID, priority, link_complete_req, last_date, user_id)
                                    SELECT control_sys, source, target, data, transactionID, priority, complete_req, last_date, user_id
                                    FROM {tn}
                                    WHERE control_sys = ?
                                    AND target = ?
                                    AND NOT EXISTS (
                                        SELECT a.*
                                        FROM {tn} AS a
                                        INNER JOIN {tu} AS b ON a.transactionID = b.transactionID AND a.control_sys = b.control_sys
                                    );""".format(tn=TB_COMM,tu=TB_CEVENT),(idst['sysID'], idst['system_type']))
            
            ### NEW EVENTS >> COMMS QUEUE
                
                ## insert sample data
                #conn.execute("""INSERT INTO {tu} (control_sys, source, target, data, priority, user_id, event_config, link_complete_req)
                #                VALUES
                #                (7010002, 31, 13, "data ish", 1, 1, 1, 1),
                #                (7010002, 31, 13, "more data wee", 1, 1, 1, 1),
                #                (7010002, 31, 13, "bingo even more data", 1, 1, 1, 1)
                #            ;""".format(tu=TB_CEVENT))
                
                # generate transactionID in events
                # TODO: test consistency of transactionID generated here and in Django
                # TODO: update fails if no event type 
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
                                    WHERE a.control_sys = ?
                                    AND a.source = ?
                                    AND NULLIF(a.complete,0) IS NULL
                                    AND a.transactionID IS NOT NULL
                                    AND NOT EXISTS (
                                        SELECT *
                                        FROM {tn} AS b
                                        INNER JOIN {tu} AS c ON b.control_sys = c.control_sys AND b.transactionID = c.transactionID
                                        WHERE a.transactionID = b.transactionID
                                    )
                                    ;""".format(tn=TB_CEVENT,tu=TB_COMM),(idst['sysID'], idst['system_type']))
  
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
                                        AND NULLIF({tu}.complete,0) IS NULL
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
                                        AND NULLIF({tu}.complete,0) IS NULL
                                    );
                            """.format(tu=TB_CEVENT, ts=TB_COMM))
            
            #### Test
            #print ">>>>>>>>>>>>>>>>>>>>>> EVENTS"
            #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_CEVENT)):
            #    print row
            #print ">>>>>>>>>>>>>>>>>>>>>> COMMS QUEUE"
            #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_COMM)):
            #    print row
            
########### Return JSON comms queue for API PUT (UPDATE) and POST

            # over write row_factory to return JSON
            conn.row_factory = dict_factory
            cur = conn.cursor()

            ### get JSON comms events that need API GET - e.g. events generated locally requiring completion at API
            
            # define fields for select
            #fields = "control_sys, meter, data, transactionID, source, target, priority, complete_req, complete, URI"
            fields = "meter, transactionID, complete"
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE comm_sent = 1
                        AND complete_req = 1
                        AND NULLIF(complete,0) IS NULL
                        AND URI NOT NULL
                        AND target < ?
                        ORDER BY priority DESC;
                        """.format(tn=TB_COMM,tf=fields),(idst['system_type'],))
            
            api_get = cur.fetchall()

            ### get JSON comms events that need API POST (e.g. originating below API)
            
            # define fields for select
            fields = "control_sys, meter, data, transactionID, source, target, priority, complete_req, complete"
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE NULLIF(comm_sent,0) IS NULL
                        AND URI IS NULL
                        AND target < ?
                        ORDER BY priority DESC;
                        """.format(tn=TB_COMM,tf=fields),(idst['system_type'],))
            
            api_post = cur.fetchall()
            
            ### get JSON comms events that need API PUT (UPDATES) (e.g. originating from API)
            
            # define fields for select
            #fields = "sysID, meter, data, transactionID, source, target, priority, complete_req, complete, URI"
            fields = "control_sys, transactionID, data, complete, complete_req, URI"
            
            # get data for comms sync
            cur.execute("""SELECT {tf} FROM {tn}
                        WHERE complete = 1
                        AND NULLIF(comm_sent,0) IS NULL
                        AND complete_req = 1
                        AND URI NOT NULL
                        ORDER BY priority DESC;
                        """.format(tn=TB_COMM,tf=fields))
            
            api_put = cur.fetchall()
            
            # return pu and post JSON
            ret_val = (api_put, api_post, api_get)
            
            
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
    
    finally:
        #### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_CEVENT)):
        #    print row
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=TB_COMM)):
        #    print row
        conn.close()
    
    return ret_val


def get_policies(tb_pol, tb_ceconf, idst):
    """
    Get policies associated with control unit
    > policy table, event config table, idst
    < policies, eventconfig
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get policies (%s) and event config (%s)' % (script_file,func_name,tb_pol,tb_ceconf))

    try :
        # connect to / create db
        conn = create_connection(db)
        
        # over write row_factory to return JSON
        conn.row_factory = dict_factory
        
        cur = conn.cursor()
        
        # get data
        cur.execute("""SELECT id, name, policy_data, default_event
                    FROM {tn}
                    WHERE user_id = ?
                    ;""".format(tn=tb_pol),(idst['user_id'],))
        policies = cur.fetchall()
        
        cur.execute("""SELECT *
                    FROM {tn}
                    WHERE user_id = ?
                    ;""".format(tn=tb_ceconf),(idst['user_id'],))
        eventconfig = cur.fetchall()
        
    except sqlite3.OperationalError as e:
        logging.debug('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
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
        
    return policies, eventconfig


def manage_event(table, user_id, method = None, data = None):
    """
    Manage events 
    > table, method (last_event, ...), data
    < last event
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Manage event method %s (%s)' % (script_file,func_name,method,table))

    try :
        # connect to / create db
        conn = create_connection(db)
        
        # over write row_factory to return JSON
        conn.row_factory = dict_factory
        
        # connection object as context manager
        with conn:
            
            cur = conn.cursor()
            
            # get last event
            if method == 'last_event':
                
                # get data
                cur.execute("""SELECT *
                            FROM {tn}
                            WHERE event_config = ?
                            ORDER BY last_date DESC
                            LIMIT 1
                            ;""".format(tn=table),(data,))
                rdata = cur.fetchone()
            
            # insert event
            else:
        
                # build dynamic insert statement components
                insert3 = insert_statement(user_id, db, table, data)
                
                #print insert3[0]
                #print insert3[1]
                #print insert3[2][0]
        
                cur.execute("""INSERT INTO {tn}({tf})
                            VALUES ({ih})
                            ;""".format(tn=table,tf=insert3[0],ih=insert3[1]),insert3[2][0])
                
                rdata = cur.lastrowid
                
    # connection object using 'with' will rool back db on exception and close on complete
    except sqlite3.IntegrityError as e:
        logging.error('%s:%s: SQL IntegrityError: %s' % (script_file,func_name,e))
        raise e
        #return False 
        
    except sqlite3.OperationalError as e:
        logging.debug('%s:%s: SQLite Operational Error: %s' % (script_file,func_name,e))
        raise e
        #return False
        
    except sqlite3.ProgrammingError as e:
        logging.error('%s:%s: SQLite Programming Error: %s' % (script_file,func_name,e))
        raise e
        #return False
    
    finally:
        ##### Test
        #for row in conn.execute('SELECT * FROM {tn}'.format(tn=table)):
        #    print row
            
        conn.close()
        
    return rdata
