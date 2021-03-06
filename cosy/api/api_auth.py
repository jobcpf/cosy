"""
Module ...

@Author: 
@Date: 

"""

################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os
import sys
import json
import time

import requests
from requests.auth import HTTPBasicAuth

# Import custom modules
import data.data_api as datp

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, BASE_URL, TOKEN_URL
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################

# create database connection
def get_new_token(token3 = None, user_id = False):
    """
    Retrieve an access token for API:
    1. use refresh_token if token3 passed, OR
    2. use username:password from db.user if 401 or no token3
    3. insert token into db.auth
    > [token3 ]
    < (True, token3), (False, Error Code)
    token3 = (userID, access_token, refresh_token)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API access token' % (script_file,func_name))
    
    # logic for refresh token vs u/p authorisation control
    up_auth = True
    user_details = False
    
    ## if token3 passed request auth token using refresh token
    if token3 is not None:
        
        # get id for token user
        user_id = token3[0]
        
        # get user5 for authed user from db.user
        user_details = datp.get_api_user(user_id)
        
        # dont use u/p auth
        up_auth = False
        
        # build auth credentials
        params = {'grant_type':'refresh_token',
                'refresh_token':token3[2]
                }
        
        r = requests.post('%s%s' % (BASE_URL,TOKEN_URL), data=params, auth=HTTPBasicAuth(user_details['client_id'], user_details['client_secret']))
        
        # test if refresh token call successful
        if r.status_code == requests.codes.unauthorized:
            logging.error('%s:%s: Refresh token unauthorised. Status Code: %s' % (script_file, func_name, r.status_code))
            
            # revert to u/p auth
            up_auth = True
    
    ## request auth token using username:password
    if up_auth :
        
        if not user_details :
            # get user5 for authed user from db.user
            user_details = datp.get_api_user(user_id = user_id)
        
        # check for user details - TODO: no function datp.init_user()
        if not user_details :
            logging.error('%s:%s: No user exists to retrieve token' % (script_file,func_name))
            user_details = datp.init_user()
        
        # get user id to pass
        user_id = user_details['id']
        
        # build auth credentials
        params = {'grant_type':'password',
                'username':user_details['user'],
                'password':user_details['passwd']
                }
        
        # make request
        r = requests.post('%s%s' % (BASE_URL,TOKEN_URL), data=params, auth=HTTPBasicAuth(user_details['client_id'], user_details['client_secret']))
    
    # return based on response
    if r.status_code == requests.codes.ok :
        
        if r.headers['Content-Type'] in ['application/json'] :
            
            # insert token into db.auth
            rbool, token3 = datp.insert_token(user_id, r.json())
            
            if rbool:
                # returns token3 or False
                return (True, token3)
            else:
                return (False, 'db insert error')
            
        else:
            logging.error('%s:%s: No valid JSON data API Token retrieved for %s' % (script_file,func_name,user_details['user']))
            return (False, r.headers['Content-Type'])
        
    else:
        logging.error('%s:%s: Token retrieval failed for user %s with status code %s' % (script_file,func_name,user_details['user'],r.status_code))
        return (False, r.status_code)
