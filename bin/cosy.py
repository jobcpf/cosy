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

def get_id3(TB_CONTROL, refresh = False):
    """
    Get id3 from control config and return as tuple.
    > control unit table (TB_CONTROL), [refresh cuID from API]
    < id3 (userID,cuID,sysID), False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get id3 from table: %s' % (script_file,func_name,TB_CONTROL))
    
    # get id3 from database
    id3 = data.get_control(TB_CONTROL)
    
    # if no id3 returned (re) init environment
    if not id3 or refresh:
        # initiate environment
        id3 = eni.init_environment()
        # populate environment config
        env_conf = eni.config_environment(id3)
        
    return id3


def comm_sync(id3):
    """
    Sync comms with API
    > 
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Sync Comms Queue for user id: %s control unit id: %s' % (script_file,func_name,id3[0],id3[1]))
    
    # get API call for comm queue
    comm_api_list = datp.get_api_config(id3[0], TB_APICONF, False, COMM_API)
    
    # iterate calls 
    for comm_call in comm_api_list :
        
        # build API call URI
        api_call = '%s%s%s' % (BASE_URL,API_BASE,comm_call[0])
        
        # append optional elements to API call URI
        if comm_call[1] :
            api_call += "%s/" % id3[1]
        
        # retrieve data from API
        data_json = apac.api_call(api_call, id3[0])
        
        # insert data if returned
        if data_json :
            data_inserted = data.insert_data(id3[0], comm_call[4], data_json)
            
            if data_inserted :
                return data_inserted

    # catch all return
    logging.error('%s:%s: Could not sync comms queue for user id: %s control unit id: %s' % (script_file,func_name,id3[0],id3[1]))
    return False


################## Script ###################################### Script ###################################### Script ####################

func_name = None
logging.debug('%s:%s: >>>>>>>>>>>>>>>>>>>>>>>> Execute control script <<<<<<<<<<<<<<<<<<<<<<<<' % (script_file,func_name))
print ">>>>>>>>>>>>>>>>>>>>>> ARGO NAUGHTY FERRET BINGLE <<<<<<<<<<<<<<<<<<<<<<<"


# get id3 from database
id3 = get_id3(TB_CONTROL)
print id3

comm_sync = comm_sync(id3)
print comm_sync

comms_json_list = data.manage_comms(id3)


#update confirmed
updated = []

for comm_json in comms_json_list:
    
    # get API call from JSON
    api_call = comm_json.pop('URI')
    
    # make API call
    api_updated = apac.api_call(api_call, id3[0], put = comm_json)
    
    if api_updated :
        updated.append(api_updated['transactionID'])

comms_updated = data.manage_comms(id3,updated)



print comms_updated




