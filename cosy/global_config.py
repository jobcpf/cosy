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
    base_url = 'http://172.16.32.40:8000'
    
    ## logging
    use_logging = True
    logdir = '/home/squirrel/dev/squirrel_dev/cosy_dev'
    logfile = "%s/cosydev.log" % logdir
    logging.basicConfig(filename=logfile,level=logging.DEBUG)


################## Variables #################################### Variables #################################### Variables ##################


# control unit - TODO: bring in from file/sys env
control_unit = 1

# logging
now_file = time.strftime('%Y%m%d_%H%M%S') # datetime for appending to file names

# API Auth / Access
token_url = '/o/token/'
api_base = '/api/0.1'

# initial API access call to retrieve API Config
api_conf = '/sys/api/'

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
DB_DATA = 'cosy_data.sqlite' # database for system data


### Temp

# Application Credentials
client_id = '4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW'
client_secret = 'q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI'



################## Functions ###################################### Functions ###################################### Functions ####################



