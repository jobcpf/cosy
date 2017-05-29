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
#import time
#from datetime import datetime
#import requests
#import json

# Import custom modules
#import api.api_auth as apa
#import api.api_access as apac
#import data.data_api as datp
#import data.data_init as dati
#import data.data as data
#import env.env_init as eni
#import envmon.envmon as em
#import api.comm as comm

import cosy_run as crun

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, TB_CONTROL
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################


################## Script ###################################### Script ###################################### Script ####################

# CRONTAB: */5 * * * * ~/dev/cosy/bin.cosy.py >/dev/null

func_name = None
logging.debug('%s:%s: >>>>>>>>>>>>>>>>>>>>>>>> Execute control script <<<<<<<<<<<<<<<<<<<<<<<<' % (script_file,func_name))
#print ">>>>>>>>>>>>>>>>>>>>>> ARGO NAUGHTY FERRET BINGLE <<<<<<<<<<<<<<<<<<<<<<<"

# initial conditions
id6 = None
token3 = None

# call script run script
rbool, id6, token3 = crun.cosy_run(id6, token3)

print 'cosy_run: ',rbool

