#!/usr/bin/env python
"""
Global configuration data for cosy.

@Author: job
@Date: 10/05/17

"""

# Standard import modules
import os
import time
import logging
import json

################## Environment #################################### Environment #################################### Environment ##################

ENV = 2 #None

# get script file path to determine environment
if ENV is None and 'squirrel' in os.path.dirname(os.path.realpath(__file__)) :
    print "Executing on Squirrel dev environment"
    ENV = 1

################## Env Variables #################################### Env Variables #################################### Env Variables ##################

if ENV == 1 : # dev environment on squirrel
    
    ## Database - sqlite
    DB_PATH = '/data/datashare'
    SYS_DETAIL = '/home/squirrel/dev/cosy/script/detail.json'
    SYS_SELECT = 0
    AUTH_DETAIL = '/home/squirrel/dev/cosy/script/auth.json'
    AUTH_SELECT = 0
    
    ## Path & URL
    PID_FILE = '/var/mylog/daemon-cosy.pid'
    BASE_URL = 'http://172.16.32.40:8000'
    
    ## logging
    use_logging = True
    logdir = '/home/squirrel/dev/squirrel_dev/cosy_dev'
    logfile = "%s/cosydev.log" % logdir
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    
    ## Temp / Test
    SPOOF_DATA = True

elif ENV == 2 : # dev environment on squirrel using Apache
    
    ## Database - sqlite
    DB_PATH = '/data/datashare'
    SYS_DETAIL = '/home/squirrel/dev/cosy/script/detail.json'
    SYS_SELECT = 0
    AUTH_DETAIL = '/home/squirrel/dev/cosy/script/auth.json'
    AUTH_SELECT = 0
    
    ## Path & URL
    PID_FILE = '/var/mylog/daemon-cosy.pid'
    BASE_URL = 'http://www.grid-monitor.co.uk'
    
    ## logging
    use_logging = True
    logdir = '/home/squirrel/dev/squirrel_dev/cosy_dev'
    logfile = "%s/cosydev.log" % logdir
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    
    ## Temp / Test
    SPOOF_DATA = True

else : # pi environment
    
    ## Database - sqlite
    DB_PATH = '/home/pi/cosy'
    SYS_DETAIL = '/home/pi/cosy/script/detail.json'
    SYS_SELECT = 1
    AUTH_DETAIL = '/home/pi/cosy/script/auth.json'
    AUTH_SELECT = 1
    
    ## Path & URL
    PID_FILE = '/tmp/daemon-cosy.pid'
    BASE_URL = 'http://www.grid-monitor.co.uk'
    #BASE_URL = 'http://172.16.32.40:8000'
    
    ## logging
    use_logging = True
    logdir = '/home/pi'
    logfile = "%s/cosydev.log" % logdir
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    
    ## Temp / Test
    SPOOF_DATA = False


################## Variables #################################### Variables #################################### Variables ##################

# Daemon
BASE_SLEEP = 300 # (seconds, 300s = 5min) base sleep period for Daemon re-runs

# logging
now_file = time.strftime('%Y%m%d_%H%M%S') # datetime for appending to file names

# API Auth / Access
TOKEN_URL = '/o/token/'
API_BASE = '/api/0.1'

# API initiation identifiers
CU_INIT = 'CUinit' # Root API Call indentifier for control unit registration URL
API_INIT = 'APIinit' # Root API Call indentifier for API detail URL
SYS_DEFAULT = 31111 # default system type if not aquired from details.json

# API call IDs
COMM_API = 2 # cosy_api.sqlite.apiaccessconfig.id for API comm call GET, PUT, POST
COMMS_API = 17 # cosy_api.sqlite.apiaccessconfig.id for API comms call MULTIPLE GET, PUT, POST

## Database - sqlite
DB_API = 'cosy_api.sqlite' # database for API access credentials - TODO: encrypt
TB_APICONF = 'apiaccessconfig'

DB_DATA = 'cosy_data.sqlite' # database for system data
TB_CONTROL = 'controlunit' # control unit details table
TB_COMM = 'commsqueue' # control unit details table
TB_CEVENT = 'controlevent' # control unit details table

TB_POL = 'controlpolicy' # policy data
TB_CECONF = 'controleventconfig' # control event configuration

# Policies
POL_REFID = 6 # Daemon run Policy ID
POL_SLEEP = 300 # (s) Default Daemon run interval

POL_CONF = 5 # Configuration Policy ID
POL_INT = 86400 # (s) 86400 = 24hrs Default Configuration refresh interval if none passed

POL_ENV = 3 # Environment Policy ID

### Temp
#
#
#
#details = [{'os':'4.10.8-200.fc25.x86_64',
#           'hardware':'HP MicroServer',
#           'system_type':31,
#           'uid':0000000000000000
#           },
#          {'os':'raspberrypi 4.9.24-v7+',
#           'hardware':'Raspberry Pi v3B',
#           'system_type':31,
#           'uid':0000000000000001
#           }]
#
#with open(SYS_DETAIL,"w") as outfile:
#    json.dump(details,outfile)
#
#
#auth = [{'user':'apitest',
#        'passwd':'buggeryouall',
#         'client_id':'4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW',
#         'client_secret':'q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI',
#        },{'user':'piauth',
#        'passwd':'bingowing',
#         'client_id':'4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW',
#         'client_secret':'q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI',
#        }]
#
#with open(AUTH_DETAIL,"w") as outfile:
#    json.dump(auth,outfile)



#env_config = {
#    'digital':None,
#    'analogue':{
#        'temp1':{
#                'channel':1,
#                'type':'temp',
#                },
#        'temp2':{
#                'channel':2,
#                'type':'temp',                
#                },
#        'light1':{
#                'channel':0,
#                'type':'light',                
#                },
#        'light2':{
#                'channel':7,
#                'type':'light',                
#                },
#        'moist1':{
#                'channel':3,
#                'type':'moisture',                
#                },
#        }
#}
#print = json.loads(default_event['event_action'])



################## Functions ###################################### Functions ###################################### Functions ####################
