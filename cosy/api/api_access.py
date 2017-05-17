#!/usr/bin/env python
"""
Module ...

@Author: 
@Date: 

api_call: generic API call retrieving JSON


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
    > 'api call identifier', [user_id], 
    < json, http status code, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API Access details from API using Token Auth' % (script_file,func_name))
    
    # attempt to get existing token with or without user ID
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
            r = requests.get(api_call, headers=auth_header)
            
            # check for unauthorised using token
            if r.status_code == requests.codes.unauthorized:
                logging.debug('%s:%s: API data retrieval unauthorised with token. Status Code: %s' % (script_file,func_name,r.status_code))
                
                get_new_token = True
                
        if token3 is None or get_new_token:
            
            # get new token (refresh > u:p)
            token3 = apa.get_new_token(token3) # get new token and add to db
            
            # build auth header
            auth_header = {'Authorization': 'Bearer %s' % token3[1]}
            
            # make request
            r = requests.get(api_call, headers=auth_header)
            
            # check for unauthorised using token
            if r.status_code == requests.codes.unauthorized:
                logging.error('%s:%s: User (id: %s) not authorised for API call. Status Code: %s' % (script_file,func_name,token3[0],r.status_code))
                return False
        
        # capture status codes from all calls
        if r.status_code == requests.codes.not_found:
            logging.error('%s:%s: API resource not found. Status Code: %s' % (script_file,func_name,r.status_code))
            return False
            
        if r.headers['Content-Type'] in ['application/json'] :
            
            # update db.apiaccessconfig
            return r.json()
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            return False
    
    except requests.exceptions.ConnectionError as e:
        logging.error('%s:%s: NewConnectionError' % (script_file,func_name))
        return False
