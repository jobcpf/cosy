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

# API call IDs
COMM_API = 2 # cosy_api.sqlite.apiaccessconfig.id for API comm call GET, PUT, POST

#sys_conf = '/sys/conf/'
#sys_event_type = '/sys/et/'
#
#comm = '/comm/%s/' % control_unit # TODO: populate all API calls aside from this from initial comm
#env_pol = '/env/pol/%s/' % control_unit
#env_conf = '/env/conf/'
#
#mets = '/mets/%s/' % control_unit
#metr = '/met/' # requires meter id
#met_pol = '/met/pol/%s/' % control_unit
#met_conf = '/met/conf/'

## Database - sqlite
DB_API = 'cosy_api.sqlite' # database for API access credentials - TODO: encrypt
TB_APICONF = 'apiaccessconfig'

DB_DATA = 'cosy_data.sqlite' # database for system data
TB_CONTROL = 'controlunit' # control unit details table
TB_COMM = 'commsqueue' # control unit details table
TB_CEVENT = 'controlevent' # control unit details table

### Temp



################## Functions ###################################### Functions ###################################### Functions ####################



