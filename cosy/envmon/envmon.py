"""
Environmental Monitoring for cosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import time
import json

# temp
from random import randint


# Import custom modules
import data.data as data


################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, TB_CEVENT
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################

def envmon_data(id6):
    """
    Sync comms with API
    > id6
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Generate Environmental Data for user id: %s control unit id: %s' % (script_file,func_name,id6['user_id'],id6['sysID']))
    
    # generate envdata
    envdata = {
        'temp1':randint(10,50),
        'temp2':randint(10,50),
        'temp3':randint(10,50),
        'temp4':randint(10,50),
        'temp5':randint(10,50),
    }
    
    data_json = json.dumps(envdata)
    
    
    event = {
            'control_sys':id6['sysID'],
            'event_config':'1',
            'parent_event':None,
            'source':id6['system_type'],
            'target':13,
            'data':data_json,
            'transactionID':None,
            'priority':1,
            'link_complete_req':1,

    }
    
    # log to control event
    data_inserted = data.insert_data(id6['user_id'], TB_CEVENT, event)
    
    return True


################## Script ###################################### Script ###################################### Script ####################




