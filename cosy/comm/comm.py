"""
Comms Script for cosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import time

# Import custom modules
import api.api_access as apac
import data.data_api as datp
import data.data as data

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, TB_APICONF, COMM_API, COMMS_API, BASE_URL, API_BASE # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################

def comm_sync(idst, token3):
    """
    Sync comms with API
    > idst, token3
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Sync Comms Queue for user id: %s control unit id: %s' % (script_file,func_name,idst['user_id'],idst['sysID']))
    
    rmsg = "Comm Sync completed: "
    
### GET API calls from db
    
    ## comms list API call
    
    # get API call for comm queue
    comm_api_list = datp.get_api_config(idst['user_id'], TB_APICONF, init = False, api_id = COMM_API)
    
    # build API call URI using first call (should only be one)
    api_comm_call = '%s%s%s' % (BASE_URL,API_BASE,comm_api_list[0][0])
    
    # append optional elements to API call URI
    if api_comm_call[1] :
        api_comm_call += "%s/" % idst['sysID']
    
    ## multiple get/put API call
    
    # get API call for comm queue
    comm_api_list = datp.get_api_config(idst['user_id'], TB_APICONF, init = False, api_id = COMMS_API)
    
    # build API call URI using first call (should only be one)
    api_comms_call = '%s%s%s' % (BASE_URL,API_BASE,comm_api_list[0][0])
    
    # append optional elements to API call URI
    if api_comms_call[1] :
        api_comms_call += "%s/" % idst['sysID']
    
### GET from API
    
    # retrieve data from API
    rbool, rdata, token3 = apac.api_call(api_comm_call, token3 = token3)
    
    # insert data if returned
    if rbool :
        data_inserted = data.manage_comms(idst, data_json = rdata, method = 'insert')
        
        rmsg += "GET (all), "
    
    elif rdata != 404:
        # exit sync and return response if error
        return (rbool, rdata, token3)
    
### UPDATE API
    
    # get list of comms items requiring API update
    comms_putpostget = data.manage_comms(idst)
    
    # updated list to pass
    update_list = []
    
## API PUT (UPDATE)
    
    # api call for each PUT in list TODO: put all items at once.
    for comm_json in comms_putpostget[0]:
        
        # get API call from JSON
        api_uri = comm_json.pop('URI')
        
        # make API call
        rbool, rdata, token3 = apac.api_call(api_uri, token3 = token3, method = 'PUT', json = comm_json)
        
        if rbool :
            update_list.append((rdata['URI'],rdata['complete'],rdata['control_sys'],rdata['transactionID']))
            
            rmsg += "PUT, "
            
        elif rdata != 404:
            # exit sync and return response if error
            return (rbool, rdata, token3)
    
### API PUT (UPDATE) (MULTIPLE by sysID, transactionID)
#    
#    # api call for each PUT in list TODO: put all items at once.
#    comm_json = comms_putpostget[0]
#    
#    print comm_json
#    
#    # make API call
#    api_response = apac.api_call(api_comms_call, user_id = idst['user_id'], method = 'PUT', json = comm_json)
#    
#    if api_response[0] :
#        # iter responses and append for sent/update
#        for response in api_response[1] :
#            update_list.append((response['URI'],response['complete'],response['control_sys'],response['transactionID']))    


## API POST

    # api call for each POST in list TODO: put all items at once.
    for comm_json in comms_putpostget[1]:
        
        # make API call
        rbool, rdata, token3 = apac.api_call(api_comm_call, token3 = token3, method = 'POST', json = comm_json)
        
        if rbool :
            update_list.append((rdata['URI'],rdata['complete'],rdata['control_sys'],rdata['transactionID']))
            
            rmsg += "POST, "
        
        elif rdata != 404:
            # exit sync and return response if error
            return (rbool, rdata, token3)
        
## API POST (MULTIPLE by sysID, transactionID)
    #...

## API GET 
    
    ## api call for each GET in list
    #for comm_json in comms_putpostget[2]:
    #    
    #    # get API call from JSON
    #    api_uri = comm_json.pop('URI')
    #    
    #    # make API call
    #    api_response = apac.api_call(api_uri, user_id = idst['user_id'], method = 'GET', json = comm_json)
    #    
    #    if api_response[0] :
    #        update_list.append((api_response[1]['URI'],api_response[1]['complete'],api_response[1]['control_sys'],api_response[1]['transactionID']))
        

## API GET (MULTIPLE by sysID, transactionID)

    # api call for each GET in list
    if comms_putpostget[2]:
        
        print comms_putpostget[2]
        
        # make API call
        rbool, rdata, token3 = apac.api_call(api_comms_call, token3 = token3, method = 'GET', json = comms_putpostget[2])
        
        if rbool :
            # iter responses and append for sent/update
            for response in rdata :
                update_list.append((response['URI'],response['complete'],response['control_sys'],response['transactionID']))
                
            rmsg += "GET (by sysID), "
        
        elif rdata != 404:
            # exit sync and return response if error
            return (rbool, rdata, token3)
        
## CONFIRM API Updated

    if update_list :
        # Mark comms and events as sent
        comms_updated = data.manage_comms(idst, data_json = update_list, method = 'updatelist')
        #return (True, rmsg, token3)
    
    return (True, rmsg, token3)


################## Script ###################################### Script ###################################### Script ####################
