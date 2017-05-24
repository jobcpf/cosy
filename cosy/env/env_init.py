"""
Environment Builder for COSY

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import json

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
    if api_setup[0]:
    
        # get available API calls
        api_json = apac.api_call(api_setup[1][API_INIT])
        
        # insert to db
        if api_json[0] :
        
            # insert json
            api_updated = datp.insert_data(user_id,TB_APICONF,api_json[1])
            return True
    
    # catchall return
    logging.error('%s:%s: Initiate API failed' % (script_file,func_name))
    return False



def init_control(user_id):
    """
    Initiate control unit
    > user_id
    < id6 {'status': u'OK',
           'user_id': 1,
           'status_bool': 1,
           'URI': u'http://172.16.32.40:8000/api/0.1/env/reg/710011/',
           'sysID': 710011,
           'system_type': 31},
           False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate control unit details for user: %s' % (script_file,func_name,user_id))
        
    # get control unit call from API root
    api_response = apac.api_call('%s%s' % (BASE_URL,API_BASE))
    
    # if details returned from API
    if api_response[0]:
        # get control unit data from API
        api_response = apac.api_call(api_response[1][CU_INIT])
        
        if api_response[0] :
            
            # get system details from file
            with open(SYS_DETAIL) as json_file:    
                detail_json = json.load(json_file)
            
            api_response[1][0]['details'] = str(detail_json)
            api_response[1][0]['system_type'] = detail_json.get('system_type',SYS_DEFAULT)
            
            # put system details & type to API
            api_response = apac.api_call(api_response[1][0]['URI'], user_id = user_id, method = 'PUT', json = api_response[1][0])
            
            if api_response[0] :
                
                # insert data to db
                control_inserted = data.insert_data(user_id, TB_CONTROL, api_response[1])
                
                # enforce self to cuID returned by API
                sysID_self = data.manage_control(user_id, TB_CONTROL, api_response[1]['sysID'])
                
                if sysID_self:
                    
                    # build id6
                    id6  = {'status': api_response[1]['status'],
                            'user_id': user_id,
                            'status_bool': api_response[1]['status_bool'],
                            'URI': api_response[1]['URI'],
                            'sysID': api_response[1]['sysID'],
                            'system_type': api_response[1]['system_type']}
                    
                    return id6
    
    # catch all return
    logging.error('%s:%s: Initiate control unit failed for user: %s' % (script_file,func_name,user_id))
    return False



def init_environment():
    """
    Test environment and initiate where required.
    > 
    < id6
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate environment.' % (script_file,func_name))
    
    ## test for databases and create if not present
    for db_name, db_sql_dict in DATABASES.iteritems() :
        
        if not os.path.isfile(os.path.join(DB_PATH,db_name)) :
            create_dbs = dati.init_db(DATABASES)
            
    logging.debug('%s:%s: Initiate user.' % (script_file,func_name))
    
    # get system details from file
    with open(AUTH_DETAIL) as json_file:    
        auth_json = json.load(json_file)
    
    # register user
    user3 = dati.init_user('user', auth_json['user'], auth_json['passwd'])
    
    logging.debug('%s:%s: Initiate API for user: %s' % (script_file,func_name,user3[0]))
    # init API for user
    api_init = init_api(user3[0])
    
    logging.debug('%s:%s: Initiate control unit for user: %s' % (script_file,func_name,user3[0]))
    # init control unit database
    id6 = init_control(user3[0])
    
    # return user ID and cuID
    return id6



def config_environment(id6):
    """
    Import environment configuration data (policy, config, registers)
    > id6
    < True
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Configure environment.' % (script_file,func_name))
    
    # get API calls marked as init
    api5_list = datp.get_api_config(id6['user_id'], TB_APICONF, init=True)
    
    # iterate calls 
    for api5 in api5_list :
        
        # build API call URI
        api_call = '%s%s%s' % (BASE_URL,API_BASE,api5[0])
        
        # append optional elements to API call URI
        if api5[1] :
            api_call += "%s/" % id6['sysID']
        
        # retrieve data from API
        api_response = apac.api_call(api_call, id6['user_id'])
        
        # insert data if returned
        if api_response[0] :
            data_inserted = data.insert_data(id6['user_id'], api5[4], api_response[1])
            
            if data_inserted :
                continue
        
        # catch all error
        logging.error('%s:%s: API data issue for API call: %s' % (script_file,func_name,api_call))
        
    return True



def get_id6(TB_CONTROL, refresh = False):
    """
    Get id6 from control config and return as tuple.
    > control unit table (TB_CONTROL), [refresh cuID from API]
    < id6, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get id6 from table: %s' % (script_file,func_name,TB_CONTROL))
    
    # get id6 from database
    id6 = data.get_control(TB_CONTROL)
    
    if id6 and not refresh:
        # push status of control unit to API (test API)
        api_response = apac.api_call(id6['URI'], user_id = id6['user_id'], method = 'PUT', json = id6)
        
        if api_response[0]:
            return id6
    
    # catch all re-init all
    id6 = init_environment()
    if id6 :
        # populate environment config
        env_conf = config_environment(id6)
        if env_conf :
            return id6
    
    return False
