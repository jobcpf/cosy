#!/home/squirrel/virtualenvs/cosy_env/bin/python
"""
Call Script for cosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys

import requests
import json

# execute module
sys.path.append("/home/squirrel/dev/cosy/cosy") # append python project directory root

# Import custom modules
import api.api_auth as apa
import api.api_access as apac
import data.data_api as datp
import data.data_init as dati
import data.data as data
import env.env_init as eni

################## Variables #################################### Variables #################################### Variables ##################

from global_config import * # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# set database sql dictionary
#from data.db_sql import DATABASES
# set up user for API auth
#from auth import USER, PASSWD

################## Functions ###################################### Functions ###################################### Functions ####################

def comm_sync(id6):
    """
    Sync comms with API
    > id6
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Sync Comms Queue for user id: %s control unit id: %s' % (script_file,func_name,id6['user_id'],id6['sysID']))
    
### GET from API
    
    # get API call for comm queue
    comm_api_list = datp.get_api_config(id6['user_id'], TB_APICONF, False, COMM_API)
    
    # iterate calls [should only be one]
    for comm_call in comm_api_list :
        
        # build API call URI
        api_call = '%s%s%s' % (BASE_URL,API_BASE,comm_call[0])
        
        # append optional elements to API call URI
        if comm_call[1] :
            api_call += "%s/" % id6['sysID']
        
        # retrieve data from API
        api_response = apac.api_call(api_call, user_id = id6['user_id'])
        
        # insert data if returned
        if api_response[0] :
            data_inserted = data.manage_comms(id6,insert_json=api_response[1],sent_conf=False)
        else:
            # exit sync and return response if error
            return api_response
    
### UPDATE API
    
    # get list of comms items requiring API update
    comms_putpostget = data.manage_comms(id6)
    
    #update confirmed list to pass
    sent_list = []
    
## API PUT (UPDATE)
    
    # api call for each PUT in list TODO: put all items at once.
    for comm_json in comms_putpostget[0]:
        
        # get API call from JSON
        api_uri = comm_json.pop('URI')
        
        # make API call
        api_response = apac.api_call(api_uri, user_id = id6['user_id'], method = 'PUT', json = comm_json)
        
        if api_response[0] :
            sent_list.append((api_response[1]['URI'],api_response[1]['complete'],api_response[1]['control_sys'],api_response[1]['transactionID']))
    
## API POST
    
    # api call for each POST in list TODO: put all items at once.
    for comm_json in comms_putpostget[1]:
        
        # make API call
        api_response = apac.api_call(api_call, user_id = id6['user_id'], method = 'POST', json = comm_json)
        
        if api_response[0] :
            sent_list.append((api_response[1]['URI'],api_response[1]['complete'],api_response[1]['control_sys'],api_response[1]['transactionID']))

## API GET 
    
    # api call for each GET in list
    for comm_json in comms_putpostget[2]:
        
        # get API call from JSON
        api_uri = comm_json.pop('URI')
        
        # make API call
        api_response = apac.api_call(api_uri, user_id = id6['user_id'], method = 'GET', json = comm_json)
        
        if api_response[0] :
            sent_list.append((api_response[1]['URI'],api_response[1]['complete'],api_response[1]['control_sys'],api_response[1]['transactionID']))
        
## CONFIRM API Updated
    
    if sent_list :
        # Mark comms and events as sent
        comms_updated = data.manage_comms(id6,insert_json=False,sent_conf=sent_list)
        return comms_updated
    
    return False


################## Script ###################################### Script ###################################### Script ####################

func_name = None
logging.debug('%s:%s: >>>>>>>>>>>>>>>>>>>>>>>> Execute control script <<<<<<<<<<<<<<<<<<<<<<<<' % (script_file,func_name))
print ">>>>>>>>>>>>>>>>>>>>>> ARGO NAUGHTY FERRET BINGLE <<<<<<<<<<<<<<<<<<<<<<<"

# get id6 from database
id6 = eni.get_id6(TB_CONTROL)
print 'id6: ',id6

# set status
#sysID_self = data.manage_control(id6['user_id'], TB_CONTROL, id6['sysID'], "OK")

if id6:
    comm_sync = comm_sync(id6)
    print "comms updated ",comm_sync




