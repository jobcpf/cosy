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
import api.api_auth as apa
import data.data_api as dat

################## Variables #################################### Variables #################################### Variables ##################

from global_config import * # get global variables
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################

def api_call(api_call, user_id = False):
    """
    Retrieve API Access details from API using Token Auth
    > user_id, 'api call identifier'
    < json, http status code, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API Access details from API using Token Auth' % (script_file,func_name))
    
    # get token with or without user ID
    if user_id :
        # get last registered token from db by user ID
        token3 = dat.get_api_token(user_id)
    else:
        # get last registered token from db
        token3 = dat.get_api_token()
    
    try:
        get_new_token = False
        
        # test if token returned
        if token3 is not None :
            # build auth header
            auth_header = {'Authorization': 'Bearer %s' % token3[1]}
            
            # make request
            r = requests.get('%s%s%s' % (base_url,api_base,api_call), headers=auth_header)
            
            # return based on response
            if r.status_code == requests.codes.unauthorized:
                logging.error('%s:%s: API data retrieval unauthorised. Status Code: %s' % (script_file,func_name,r.status_code))
                
                get_new_token = True
                
        if token3 is None or get_new_token:
            # get new token (refresh > u:p)
            token3 = apa.get_new_token(token3) # get new token and add to db
            
            # build auth header
            auth_header = {'Authorization': 'Bearer %s' % token3[1]}
            
            # make request
            r = requests.get('%s%s%s' % (base_url,api_base,api_call), headers=auth_header)
            
        if r.headers['Content-Type'] in ['application/json'] :
            
            # update db.apiaccessconfig
            return r.json()
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            return False
    
    except requests.exceptions.ConnectionError as e:
        logging.error('%s:%s: NewConnectionError' % (script_file,func_name))
        return False



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