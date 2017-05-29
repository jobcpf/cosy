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

# Import custom modules
import env.env_init as eni
import envmon.envmon as em
import comm.comm as comm

################## Variables #################################### Variables #################################### Variables ##################

import global_config as gc
from global_config import logging, now_file, TB_CONTROL
script_file = "%s: %s" % (now_file,os.path.basename(__file__))


################## Functions ###################################### Functions ###################################### Functions ####################

################## Script ###################################### Script ###################################### Script ####################

def cosy_run(id6 = None, token3 = None):
    """
    Run COSY script
    > 
    < 
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    if id6 is None :
        # get id6 from database
        rbool, id6, token3 = eni.get_id6(TB_CONTROL)
    
    print id6
    
    logging.debug('%s:%s: >>>>>>>>>>>>>> Run job for user id: %s control unit id: %s' % (script_file,func_name,id6['user_id'],id6['sysID']))
    
    
    ## set status
    ##sysID_self = data.manage_control(id6['user_id'], TB_CONTROL, id6['sysID'], "OK")
    #
    ## refresh environment
    ##eni.config_environment(id6[1], api_update = True)
    
    
    # generate env data
    if id6 is not None:
        env_data = em.envmon_data(id6)
        print "env data updated: ",env_data
        
    # sync comms
    if id6 is not None:
        rbool, comm_result, token3 = comm.comm_sync(id6, token3)
        
        # not authorised on GET for sysID - re-init container
        if comm_result == 403 :
            # Permissions on control unit - re-init control
            rbool, id6, token3 = eni.get_id6(TB_CONTROL, refresh = True)
        
        print "comms updated: ",comm_result
        
    return (True, id6, token3)



