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
def get_new_token(token3 = False):
    """
    Retrieve an access token for API using refresh_token if available or via username:password from db.user
    > opt token3 
    < token3 (userID, access_token, refresh_token)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API access token' % (script_file,func_name))
    
    # logic for refresh token vs up authorisation control
    up_auth = True
    
    ## request auth token using refresh token
    if token3 : # use refresh_token
        
        up_auth = False
        
        # get user id to pass
        user_id = token3[0]
        
        # build auth credentials
        params = {'grant_type':'refresh_token',
                'refresh_token':token3[2]
                }
        
        r = requests.post('%s%s' % (base_url,token_url), data=params, auth=HTTPBasicAuth(client_id, client_secret))
        
        # test if refresh token call successful & return
        if r.status_code == requests.codes.unauthorized:
            logging.error('%s:%s: Refresh token unauthorised. Status Code: %s' % (script_file, func_name, r.status_code))
            up_auth = True
        
        # get (id,user,password) for token user
        user_details = dat.get_api_user(token3[0])
    
    else: # use username:password from db.user
        
        # get (id,user,password) for authed user from db.auth
        user_details = dat.get_api_user()
        # get user id to pass
        user_id = user_details[0]
    
    ## request auth token using username:password
    if up_auth :
        
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
            inserted = dat.insert_token(user_id, r.json())
            
            # returns token3 or False
            return inserted
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved for API Token' % (script_file,func_name,user_details[1]))
            return False
        
    else:
        logging.error('%s:%s: Token retrieval failed for user %s with status code %s' % (script_file,func_name,user_details[1],r.status_code))
        return r.status_code
