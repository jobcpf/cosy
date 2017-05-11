#!/usr/bin/env python
"""
Module ...

@Author: 
@Date: 

"""

################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os
import sys

import requests
from requests.auth import HTTPBasicAuth

# Import custom modules
import data.data_api as dat

################## Variables #################################### Variables #################################### Variables ##################

from global_config import * # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################


def api_config(token3,api_call):
    """
    Retrieve API Access details from API using Token Auth
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API Access details from API using Token Auth' % (script_file,func_name))
    
    # unpack token3
    user_id = token3[0]
    auth_token = token3[1]
    
    # build auth header
    auth_header = {'Authorization': 'Bearer %s' % auth_token}
    
    # make request
    r = requests.get('%s%s%s' % (base_url,api_base,api_call), headers=auth_header)
    
    # return based on response
    if r.status_code == requests.codes.ok :
        
        if r.headers['Content-Type'] in ['application/json'] :
            
            # update db.apiaccessconfig
            return dat.insert_api_config(user_id,r.json())
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            return False
    else:
        logging.error('%s:%s: API data retrieval failed with status code %s' % (script_file,func_name,r.status_code))
        return r.status_code

    
def api_access(auth_token,api_call):
    """
    Retrieve data from API using Token Auth
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve data from API using Token Auth' % (script_file,func_name))
    
    # build auth header
    auth_header = {'Authorization': 'Bearer %s' % auth_token}
    
    # make request
    r = requests.get('%s%s%s' % (base_url,api_base,api_call), headers=auth_header)
    
    # return based on response
    if r.status_code == requests.codes.ok :
        
        if r.headers['Content-Type'] in ['application/json'] :
            
            return r.json()
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            return False
    else:
        logging.error('%s:%s: API data retrieval failed with status code %s' % (script_file,func_name,r.status_code))
        return r.status_code



"""
curl -X POST -d "grant_type=password&username=apitest&password=buggeryouall" -u"4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW:q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI" http://172.16.32.40:8000/o/token/

{
	"access_token": "agUy17UxZFR3gt2VyNxDOz7mzcohv9",
	"token_type": "Bearer",
	"expires_in": 86400,
	"refresh_token": "tv7MGCwg4VWxVAdK5IznSFccxCKCHe",
	"scope": "read write groups"
}

curl -H "Authorization: Bearer G7PUUmGQAFUok8z6A0xWnq82FKkaQ7" http://172.16.32.40:8000/api/0.1/comm/

#headers=custom_header
#{"Content-Type": "application/json"}
#custom_header = {'Authorization': 'Bearer {ACCESS_TOKEN_GOES_HERE}'}
#custom_header = {'Authorization': 'Basic 4aE5hkwDGImTothmtuJIt7nPWG7fi1q0zuIKVqFW:q0GhaHeA924ClMNBWeDHkcHql3z378iHE7uGqjfXJ90PQ83OPkPXHQskhIwa8OZgYIo41kfGddC5ckS8e39gPYwKnCmG5SPkq0lraM2TTHWGBSmWSyB2axHWmwLxt8JI'}
#custom_header = {'Accept': 'application/xml'}

"""