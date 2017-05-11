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

# create database connection
def get_new_token(refresh_token = False):
    """
    Retrieve an access token for API using refresh_token if available or via username:password from db.user
    return token3, False or Status Code
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API access token (use refresh_token: %s)' % (script_file,func_name,refresh_token))
    
    ## request auth token
    if refresh_token : # use refresh_token
        pass
    
    else: # use username:password from db.user
        
        # get (id,user,password) for authed user from db.auth
        user_details = dat.get_api_user()
        
        # check for user details
        if not user_details :
            logging.error('%s:%s: No user exists to retrieve token' % (script_file,func_name))
            user_details = dat.init_user()
        
        # build auth credentials
        params = {'grant_type':'password',
                'username':user_details[1],
                'password':user_details[2]
                }
        
        # make request
        r = requests.post('%s%s' % (base_url,token_url), data=params, auth=HTTPBasicAuth(client_id, client_secret))
    
    # return based on response
    if r.status_code == requests.codes.ok :
        
        if r.headers['Content-Type'] in ['application/json'] :
            
            # insert token into db.auth
            inserted = dat.insert_token(user_details[0], r.json())
            
            # returns token3 or False
            return inserted
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from for API Token' % (script_file,func_name,user_details[1]))
            return False
    else:
        logging.error('%s:%s: Token retrieval failed for user %s with status code %s' % (script_file,func_name,user_details[1],r.status_code))
        return r.status_code
