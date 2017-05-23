"""
Environment Builder for COSY

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys

# Import custom modules
#import api.api_auth as apa
import data.data_api as datp
import api.api_access as apac
import data.data_init as dati
import data.data as data

################## Variables #################################### Variables #################################### Variables ##################

from global_config import * # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# set database sql dictionary
from data.db_sql import DATABASES
# set up user for API auth
from auth import USER, PASSWD

################## Functions ###################################### Functions ###################################### Functions ####################


def init_api(user_id):
    """
    Retrieve API details from API Root Call
    > user3
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate API details' % (script_file,func_name))

    # retrieve API calls from API Root
    api_setup = apac.api_call('%s%s' % (BASE_URL,API_BASE))
    
    # if details returned from API Root
    if api_setup :
    
        # get available API calls
        api_json = apac.api_call(api_setup[API_INIT])
        
        # insert to db
        if api_json :
        
            # insert json
            api_updated = datp.insert_data(user_id,TB_APICONF,api_json)
            return True
    
    # catchall return
    logging.error('%s:%s: Initiate API failed' % (script_file,func_name))
    return False



def init_control(user_id):
    """
    Initiate control unit
    > user_id
    < id3 (userID,sysID,system_type), False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate control unit details for user: %s' % (script_file,func_name,user_id))
        
    # get control unit call from API root
    api_setup = apac.api_call('%s%s' % (BASE_URL,API_BASE))
    
    # if details returned from API
    if api_setup :
        # get control unit data from API
        control_json = apac.api_call(api_setup[CU_INIT])
    
        if control_json :
            control_inserted = data.insert_data(user_id, TB_CONTROL, control_json)
            
            # enforce self to cuID returned by API
            sysID_self = data.manage_control(user_id, TB_CONTROL, control_json[0]['sysID'])
            
            if sysID_self:
                return (user_id,control_json[0]['sysID'],control_json[0]['system_type'])
    
    # catch all return
    logging.error('%s:%s: Initiate control unit failed for user: %s' % (script_file,func_name,user_id))
    return False



def init_environment():
    """
    Test environment and initiate where required.
    > 
    < id3 (userID,sysID,system_type)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate environment.' % (script_file,func_name))
    
    ## test for databases and create if not present
    for db_name, db_sql_dict in DATABASES.iteritems() :
        
        if not os.path.isfile(os.path.join(DB_PATH,db_name)) :
            create_dbs = dati.init_db(DATABASES)
            
    logging.debug('%s:%s: Initiate user.' % (script_file,func_name))
    # register user
    user3 = dati.init_user('user', USER, PASSWD)
    
    logging.debug('%s:%s: Initiate API for user: %s' % (script_file,func_name,user3[0]))
    # init API for user
    api_init = init_api(user3[0])
    
    logging.debug('%s:%s: Initiate control unit for user: %s' % (script_file,func_name,user3[0]))
    # init control unit database
    id3 = init_control(user3[0])
                
    # return user ID and cuID
    return id3



def config_environment(id3):
    """
    Import environment configuration data (policy, config, registers)
    > id3
    < True
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Configure environment.' % (script_file,func_name))
    
    # get API calls marked as init
    api5_list = datp.get_api_config(id3[0], TB_APICONF, init=True)
    
    # iterate calls 
    for api5 in api5_list :
        
        # build API call URI
        api_call = '%s%s%s' % (BASE_URL,API_BASE,api5[0])
        
        # append optional elements to API call URI
        if api5[1] :
            api_call += "%s/" % id3[1]
        
        # retrieve data from API
        data_json = apac.api_call(api_call, id3[0])
        
        # insert data if returned
        if data_json :
            data_inserted = data.insert_data(id3[0], api5[4], data_json)
            
            if data_inserted :
                continue
        
        # catch all error
        logging.error('%s:%s: API data issue for API call: %s' % (script_file,func_name,api_call))
        
    return True