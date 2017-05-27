#!/usr/bin/env python
"""
Module API access

@Author: 
@Date: 

"""

################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

# Import custom modules
import api.api_auth as apa
import data.data_api as datp

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file
script_file = "%s: %s" % (now_file,os.path.basename(__file__))


################## Functions ###################################### Functions ###################################### Functions ####################

def api_call(api_call, user_id = False, method = False, json = False):
    """
    Retrieve data from API using token.
    > 'api call identifier', [user_id], 
    < response tuple: (True,json data) or (False,http status code)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Retrieve API Access details from API using Token Auth' % (script_file,func_name))
    
    # attempt to get existing token with or without user ID
    if user_id :
        # get last registered token from db by user ID
        token3 = datp.get_api_token(user_id)
    else:
        # get last registered token from db
        token3 = datp.get_api_token()
    
    try:
        get_new_token = False
        
        # test if token returned
        if token3 is not None :
            
            # build auth header
            auth_header = {'Authorization': 'Bearer %s' % token3[1]}
            
            # make request
            if method == 'GET' :
                r = requests.get(api_call, json=json, headers=auth_header)
            elif method == 'POST' :
                r = requests.post(api_call, json=json, headers=auth_header)
            elif method == 'PUT' :
                
                #print json
                r = requests.put(api_call, json=json, headers=auth_header)
                #print r.json()
                
            else :
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
            if method == 'GET' :
                r = requests.get(api_call, json=json, headers=auth_header)
            elif method == 'POST' :
                r = requests.post(api_call, json=json, headers=auth_header)
            elif method == 'PUT' :
                r = requests.put(api_call, json=json, headers=auth_header)
            else :
                r = requests.get(api_call, headers=auth_header)
            
        # capture status codes from all calls
        if r.status_code == requests.codes.unauthorized:
            logging.error('%s:%s: API data retrieval unauthorised with token. Status Code: %s' % (script_file,func_name,r.status_code))
            return (False, r.status_code)
        
        elif r.status_code == requests.codes.internal_server_error:
            logging.error('%s:%s: API caused an internal server error. Status Code: %s' % (script_file,func_name,r.status_code))
            return (False, r.status_code)
        
        elif r.status_code == requests.codes.bad_request:
            logging.error('%s:%s: Bad request to API. Status Code: %s' % (script_file,func_name,r.status_code))
            return (False, r.status_code)

        elif r.status_code == requests.codes.not_found:
            logging.error('%s:%s: Resource not found at API. Status Code: %s' % (script_file,func_name,r.status_code))
            return (False, r.status_code)
        
        elif r.status_code == requests.codes.forbidden:
            logging.error('%s:%s: Forbidden to access API. Status Code: %s' % (script_file,func_name,r.status_code))
            return (False, r.status_code)
                        
        if r.headers['Content-Type'] in ['application/json'] :
            
            # return data
            return (True,r.json())
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            return (False, r.status_code)
    
    except requests.exceptions.ConnectionError as e:
        logging.error('%s:%s: ConnectionError: %s' % (script_file,func_name,e))
        return (False, 503)
