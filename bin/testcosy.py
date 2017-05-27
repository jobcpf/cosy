#!/home/squirrel/virtualenvs/cosy_env/bin/python
"""
Test Call Script for cosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

import sys
sys.path.append("/home/squirrel/dev/cosy/cosy") # append python project directory root

# Standard import
import os.path
import time
#from datetime import datetime
#import requests
#import json

# Import custom modules
#import api.api_auth as apa
#import api.api_access as apac
#import data.data_api as datp
#import data.data_init as dati
import data.data as data
import env.env_init as eni
import envmon.envmon as em
import api.comm as comm

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, TB_CONTROL
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################


################## Script ###################################### Script ###################################### Script ####################

# CRONTAB: */5 * * * * ~/dev/cosy/bin.cosy.py >/dev/null

func_name = None
logging.debug('%s:%s: >>>>>>>>>>>>>>>>>>>>>>>> Execute control script <<<<<<<<<<<<<<<<<<<<<<<<' % (script_file,func_name))
#print ">>>>>>>>>>>>>>>>>>>>>> ARGO NAUGHTY FERRET BINGLE <<<<<<<<<<<<<<<<<<<<<<<"

# get id6 from database
gotid6, id6 = eni.get_id6(TB_CONTROL)
print 'id6: ',id6

if gotid6:
    # generate env data
    env_data = em.envmon_data(id6)
    print "env data updated ",env_data

# set status
#sysID_self = data.manage_control(id6['user_id'], TB_CONTROL, id6['sysID'], "OK")

# refresh environment
#eni.config_environment(id6[1], api_update = True)

if gotid6:
    comm_sync = comm.comm_sync(id6)
    print "comms updated ",comm_sync
