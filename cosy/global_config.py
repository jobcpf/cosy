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


################## Environment #################################### Environment #################################### Environment ##################

# get script file path to determine environment
if 'squirrel' in os.path.dirname(os.path.realpath(__file__)) :
    print "Executing on Squirrel dev environment"
    ENV = 1
    

################## Env Variables #################################### Env Variables #################################### Env Variables ##################

if ENV == 1 : # dev environment on squirrel
    
    ## Database - sqlite
    DB_PATH = '/data/datashare'
    SYS_DETAIL = '/home/squirrel/dev/cosy/script/detail.json'
    AUTH_DETAIL = '/home/squirrel/dev/cosy/script/auth.json'
    
    ## Path & URL
    BASE_URL = 'http://172.16.32.40:8000'
    
    ## logging
    use_logging = True
    logdir = '/home/squirrel/dev/squirrel_dev/cosy_dev'
    logfile = "%s/cosydev.log" % logdir
    logging.basicConfig(filename=logfile,level=logging.DEBUG)


################## Variables #################################### Variables #################################### Variables ##################

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
TB_CECONF = 'controleventconfig' # control event configuration


### Temp

#details = {'os':'4.10.8-200.fc25.x86_64',
#           'hardware':'Raspberry Pi v3B',
#           'system_type':31,
#           }
#
#with open(SYS_DETAIL,"w") as outfile:
#    json.dump(details,outfile)

#details = {'user':'apiauth',
#           'passwd':'bingowing',
#            'client_id':'4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW',
#            'client_secret':'q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI',
#           }
#
#with open(AUTH_DETAIL,"w") as outfile:
#    json.dump(details,outfile)


################## Functions ###################################### Functions ###################################### Functions ####################



