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
import env.env_init as eni
import envmon.envmon as em
import api.comm as comm

################## Variables #################################### Variables #################################### Variables ##################

import global_config as gc
from global_config import logging, now_file, TB_CONTROL
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

# update time
#now_file = time.strftime('%Y%m%d_%H%M%S')

################## Functions ###################################### Functions ###################################### Functions ####################

################## Script ###################################### Script ###################################### Script ####################

def cosy_run():
    """
    Run COSY script
    > 
    < 
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
    # get id6 from database
    gotid6, id6 = eni.get_id6(TB_CONTROL)
    
    logging.debug('%s:%s: Daemon run job for user id: %s control unit id: %s' % (script_file,func_name,id6['user_id'],id6['sysID']))
    
    # generate env data
    if gotid6:
        env_data = em.envmon_data(id6)
    
    # sync comms
    if gotid6:
        comm_sync = comm.comm_sync(id6)
        
    return True
