"""
Run script for cosy
Called periodically from cosyd as Daemon or from testcosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import time

import datetime
import json

# Import custom modules
import env.env_init as eni
import envmon.envmon as em
import comm.comm as comm
import data.data as data
import api.api_access as apac

################## Variables #################################### Variables #################################### Variables ##################

import global_config as gc
from global_config import logging, now_file, TB_CONTROL, TB_POL, TB_CECONF, POL_CONF, POL_INT, POL_REFID, POL_SLEEP, POL_ENV
script_file = "%s: %s" % (now_file,os.path.basename(__file__))


################## Functions ###################################### Functions ###################################### Functions ####################

################## Script ###################################### Script ###################################### Script ####################

def cosy_run(idst = None, token3 = None):
    """
    Run COSY script
    > 
    < 
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    pol_sleep = POL_SLEEP
    
    # starting status
    status_string = ""
    
    if idst is None :
        logging.debug('%s:%s: >>>>>>>>>>>>>> Retrieve credentials for API access <<<<<<<<<<<<<<' % (script_file,func_name))

        # get idst from database
        rbool, idst, token3 = eni.get_idst(TB_CONTROL)
        
    # run processes for idst
    if idst is not None:
        logging.debug('%s:%s: >>>>>>>>>>>>>> In-Memory Credentials for u/sys %s/%s <<<<<<<<<<<<<<' % (script_file,func_name,idst['user_id'],idst['sysID']))
        
## GET POLICIES
        
        # get all policies relevent to user id
        policies, eventconfig = data.get_policies(TB_POL, TB_CECONF, idst)
        
## GET BASE REFRESH
        
        # get policy data for daemon
        try :
            daemon_policy = json.loads([policy for policy in policies if policy["id"] == POL_REFID][0]['policy_data'])
            pol_sleep = daemon_policy['interval']
        except (KeyError, IndexError, TypeError, ValueError,) as e :
            logging.error('%s:%s: Error retrieving daemon policy for u/sys %s/%s - %s' % (script_file,func_name,idst['user_id'],idst['sysID'],e))
            
            status_string += "Daemon Policy Error (used default), "
        
## RUN CONFIG REFRESH
        
        # get policy data for config
        try :
            config_policy = json.loads([policy for policy in policies if policy["id"] == POL_CONF][0]['policy_data'])
            pol_int = config_policy['interval']
            last_config = datetime.datetime.strptime(idst['last_config'], '%Y-%m-%d %H:%M:%S.%f')
            
        except (KeyError, IndexError, TypeError, ValueError,) as e :
            logging.error('%s:%s: Error retrieving config policy for u/sys %s/%s - %s' % (script_file,func_name,idst['user_id'],idst['sysID'],e))
            pol_int = POL_INT
            last_config = datetime.datetime.now()
            
            status_string += "Config Policy Error (used default), "
            
        # update configuration 
        if datetime.datetime.now() > last_config + datetime.timedelta(seconds=pol_int) :
            logging.debug('%s:%s: Refresh configuration for u/sys %s/%s' % (script_file,func_name,idst['user_id'],idst['sysID']))
            ## refresh environment config
            rbool, idst, token3 = eni.config_environment(idst, token3, api_update = True)
        
        # flush policies
        #rbool, idst, token3 = eni.config_environment(idst, token3, api_update = True)
        
## RUN ENVIRONMENT MODULE
        
        # get policy data for environment module
        try :
            # get environment policy from policies
            env_policy = [policy for policy in policies if policy["id"] == POL_ENV][0]
            
            # get default event data from dict
            default_event = [eventcf for eventcf in eventconfig if eventcf["id"] == env_policy['default_event']][0]
            
            # get policy data
            policy_data = env_policy['policy_data']
            
            # generate environmental data
            env_data = em.envmon_data(idst, policy_data, default_event)
            print "env data updated: ", env_data
            
        except (KeyError, IndexError, TypeError, ValueError,) as e :
            logging.error('%s:%s: Error retrieving environment policy for u/sys %s/%s - %s' % (script_file,func_name,idst['user_id'],idst['sysID'],e))
            
            status_string += "Environmental Policy Error (aborted), "

        
## RUN COMMS UPDATE
        # sync comms
        rbool, comm_result, token3 = comm.comm_sync(idst, token3)
        
        if not rbool:
            status_string += "Comms error: %s, " % comm_result
        
        # not authorised on GET for sysID - re-init container
        if comm_result == 403 :
            # Permissions issue on control unit - re-init control
            rbool, idst, token3 = eni.get_idst(TB_CONTROL, refresh = True)
        
            if not rbool:
                status_string += "Error re-initialising control unit, "

        print "comms updated: ",comm_result
        
## STATUS UPDATE
        
        # if error
        if status_string :
            # log error and upload
            idst = data.manage_control(TB_CONTROL, idst['sysID'], method = 'status', data = status_string[:-2])
            
            # push status of control unit to API
            rbool, rdata, token3 = apac.api_call(idst['URI'], token3 = token3, method = 'PUT', json = idst)
            
            # if status_string has errors and not authed to update control unti at API (catch mid daemon run change in server registered control unit)
            if not rbool and rdata == 403:
                # refresh auth
                rbool, idst, token3 = eni.get_idst(TB_CONTROL,True)
            
            return (False, idst, token3, pol_sleep)
            
        # if status_bool was zero, now OK - reset
        elif not idst['status_bool']: 
            ## set status to OK
            idst = data.manage_control(TB_CONTROL, idst['sysID'], method = 'status')
            
            # push status of control unit to API
            rbool, rdata, token3 = apac.api_call(idst['URI'], token3 = token3, method = 'PUT', json = idst)
        
        
        return (True, idst, token3, pol_sleep)
            
    else: # idst is None:
        return (False, idst, token3, pol_sleep)



