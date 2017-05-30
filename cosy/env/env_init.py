"""
Environment Builder for COSY

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import time
import json
import socket

from datetime import datetime

# Import custom modules
#import api.api_auth as apa
import data.data_api as datp
import api.api_access as apac
import data.data_init as dati
import data.data as data

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, BASE_URL,API_BASE, TB_APICONF, API_INIT, CU_INIT, TB_CONTROL, SYS_DETAIL, SYS_SELECT, AUTH_DETAIL, AUTH_SELECT, DB_PATH
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# set database sql dictionary
from data.db_sql import DATABASES


################## Functions ###################################### Functions ###################################### Functions ####################


def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial


def init_api(user_id):
    """
    Retrieve API details from API Root Call
    > user_id
    < (True, None, token3), (False, None, None)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate API details' % (script_file,func_name))

    # retrieve API calls from API Root
    api_setup = apac.api_call('%s%s' % (BASE_URL,API_BASE), user_id = user_id)
    
    # if details returned from API Root
    if api_setup[0]:
    
        # get available API calls
        rbool, rdata, token3 = apac.api_call(api_setup[1][API_INIT], token3 = api_setup[2])
        
        # insert to db
        if rbool :
        
            # insert json
            api_data_updated = datp.insert_data(user_id,TB_APICONF,rdata)
            
            if api_data_updated :
                return (True, None, token3)
    
    # catchall return
    logging.error('%s:%s: Initiate API failed' % (script_file,func_name))
    return (False, None, None)



def init_control(user_id, token3):
    """
    Initiate control unit
    > user_id, token3
    < (True, idst, token3), (False, Error, token3)
    idst {'status': u'OK',
          'user_id': 1,
          'status_bool': 1,
          'URI': u'http://172.16.32.40:8000/api/0.1/env/reg/710011/',
          'sysID': 710011,
          'system_type': 31,
          'last_config: [date],}
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate control unit details for user: %s' % (script_file,func_name,user_id))
        
    # get control unit call from API root
    rbool, rdata, token3 = apac.api_call('%s%s' % (BASE_URL,API_BASE), token3 = token3)
    
    # if details returned from API
    if rbool:
        # get control unit data from API
        rbool, rdata, token3 = apac.api_call(rdata[CU_INIT], token3 = token3)
        
        if rbool :
            
            try: 
                # get system details from file
                with open(SYS_DETAIL) as json_file:    
                    list_json = json.load(json_file)
                
                # get json from list
                detail_json = list_json[SYS_SELECT]
                
                rdata[0]['details'] = str(detail_json)
                #rdata[0]['system_type'] = detail_json.get('system_type',SYS_DEFAULT) # permissive with default
                rdata[0]['system_type'] = detail_json['system_type']
                
                # get uid from function
                uid = getserial()
                rdata[0]['uid'] = uid
                #rdata[0]['uid'] = detail_json['uid']
                
                # get ip
                rdata[0]['ip'] = socket.gethostbyname(socket.gethostname())
                
            except IOError as e:
                logging.error('%s:%s: loading %s failed for user: %s' % (script_file,func_name,SYS_DETAIL,user_id))
                return (False, 'IOError', token3)
                
            except KeyError as e:
                logging.error('%s:%s: Key error in file %s %s (user: %s)' % (script_file,func_name,SYS_DETAIL, e, user_id))
                return (False, 'KeyError', token3)
                
            # put system details & type to API
            rbool, rdata, token3 = apac.api_call(rdata[0]['URI'], token3 = token3, method = 'PUT', json = rdata[0])
            
            if rbool :
                
                # insert data to db
                control_inserted = data.insert_data(user_id, TB_CONTROL, rdata)
                
                # enforce self to cuID returned by API
                idst = data.manage_control(TB_CONTROL, rdata['sysID'], method = 'self')
                
                if idst:
                    
                    # build idst from API call response
                    idst  = {'status': rdata['status'],
                            'user_id': user_id,
                            'status_bool': rdata['status_bool'],
                            'URI': rdata['URI'],
                            'sysID': rdata['sysID'],
                            'system_type': rdata['system_type'],
                            'last_config':str(datetime.now()),
                            }
                    
                    return (True, idst, token3)
    
    # catch all return
    logging.error('%s:%s: Initiate control unit failed for user: %s' % (script_file,func_name,user_id))
    return (False, None, token3)



def init_environment():
    """
    Test environment and initiate where required.
    > 
    < (True, idst, token3)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Initiate environment.' % (script_file,func_name))
    
    ## test for databases and create if not present
    for db_name, db_sql_dict in DATABASES.iteritems() :
        
        if not os.path.isfile(os.path.join(DB_PATH,db_name)) :
            create_dbs = dati.init_db(DATABASES)
        
    logging.debug('%s:%s: Initiate user.' % (script_file,func_name))
    
    # get system details from file
    try:
        with open(AUTH_DETAIL) as json_file:    
            list_json = json.load(json_file)
            
            # get json from list
            auth_json = list_json[AUTH_SELECT]
            
    except IOError as e:
        logging.error('%s:%s: loading %s failed' % (script_file,func_name,AUTH_DETAIL))
        return False
    
    # register user
    user5 = dati.init_user('user', auth_json)
    
    logging.debug('%s:%s: Initiate API for user: %s' % (script_file,func_name,user5['user']))
    # init API for user
    rbool, rdata, token3 = init_api(user5['id'])
    
    logging.debug('%s:%s: Initiate control unit for user: %s' % (script_file,func_name,user5['user']))
    # init control unit database
    rbool, idst, token3 = init_control(user5['id'], token3)
    
    return (rbool, idst, token3)



def config_environment(idst, token3, api_update = False):
    """
    Import environment configuration data (policy, config, registers)
    > idst, token3, [api_update]
    < (True, idst, token3)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Configure environment.' % (script_file,func_name))
    
    if api_update :
        # refresh api list
        rbool, rdata, token3 = init_api(idst['user_id'])
    
    # get API calls marked as init
    api5_list = datp.get_api_config(idst['user_id'], TB_APICONF, init=True)
    
    # iterate calls 
    for api5 in api5_list :
        
        # build API call URI
        api_call = '%s%s%s' % (BASE_URL,API_BASE,api5[0])
        
        # append optional elements to API call URI
        if api5[1] :
            api_call += "%s/" % idst['sysID']
        
        # retrieve data from API
        rbool, rdata, token3 = apac.api_call(api_call, token3 = token3)
        
        # insert data if returned
        if rbool :
            data_inserted = data.insert_data(idst['user_id'], api5[4], rdata)
            
            if data_inserted :
                continue
            else:
                logging.error('%s:%s: API data insert issue for API call: %s' % (script_file,func_name,api_call))
                return (False, idst, token3)
    
    # update last_config for control unit
    config_update = data.manage_control(TB_CONTROL, idst['sysID'], method = 'config')
    
    
    return (True, idst, token3)



def get_idst(TB_CONTROL, refresh = False):
    """
    Get idst from control config and return as tuple.
    > control unit table (TB_CONTROL), [refresh cuID from API]
    < (True, idst, token3), (False, Error info, token3), (False, None, None)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Get idst from table: %s' % (script_file,func_name,TB_CONTROL))
    
    # get idst from database
    #idst = data.get_control(TB_CONTROL)
    idst = data.manage_control(TB_CONTROL)
    
    if idst and not refresh:
        
        # get last registered token from db by user ID
        token3 = datp.get_api_token(idst['user_id'])
        
        # push status of control unit to API (test API)
        rbool, rdata, token3 = apac.api_call(idst['URI'], token3 = token3, method = 'PUT', json = idst)
        
        return (True, idst, token3)
    
    # catch all re-init all
    rbool, idst, token3 = init_environment()
    if rbool :
        # populate environment config
        rbool, idst, token3 = config_environment(idst, token3)
        
        if rbool :
            return (True, idst, token3)
    
    return (False, None, None)
