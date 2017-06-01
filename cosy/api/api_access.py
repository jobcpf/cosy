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

def api_call(api_call, user_id = False, token3 = None, method = None, json = False):
    """
    Retrieve data from API using token.
    > 'api call identifier', [user_id], [token3], [method: PUT|POST|GET], [json data]
    < response tuple: (True, json data, token3) or (False,http status code, token3)
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: API call (%s): %s' % (script_file,func_name,method,api_call))
    
    try:
        get_token = False
        
        # test if token returned
        if token3 is not None :
            
            # build auth header
            auth_header = {'Authorization': 'Bearer %s' % token3[1]}
            
            # make request
            if method == 'GET' :
                #print json
                r = requests.get(api_call, json=json, headers=auth_header)
            elif method == 'POST' :
                #print json
                r = requests.post(api_call, json=json, headers=auth_header)
                #print r.json()
            elif method == 'PUT' :
                #print json
                r = requests.put(api_call, json=json, headers=auth_header)
                #print r.json()
            else :
                #print json
                r = requests.get(api_call, headers=auth_header)
                #print r.json()
                
            # check for unauthorised using token
            if r.status_code == requests.codes.unauthorized:
                logging.debug('%s:%s: API data retrieval unauthorised with token. Status Code: %s' % (script_file,func_name,r.status_code))
                
                get_token = True
                
        if token3 is None or get_token:
            
            # get new token (refresh > u:p)
            rbool, token3_or_error = apa.get_new_token(token3 = token3, user_id = user_id) # get new token and add to db
            
            # check if token returned
            if rbool:
                
                # build auth header
                auth_header = {'Authorization': 'Bearer %s' % token3_or_error[1]}
                
                # make request
                if method == 'GET' :
                    r = requests.get(api_call, json=json, headers=auth_header)
                elif method == 'POST' :
                    r = requests.post(api_call, json=json, headers=auth_header)
                elif method == 'PUT' :
                    r = requests.put(api_call, json=json, headers=auth_header)
                else :
                    r = requests.get(api_call, headers=auth_header)
                    
            else:
                logging.error('%s:%s: Could not retrieve new token. Error: %s' % (script_file,func_name,token3))
                return (False, token3_or_error, None)
            
        # capture status codes from all calls
        if r.status_code == requests.codes.unauthorized: # 401
            logging.error('%s:%s: API unauthorised with token. Status Code: %s, API Call: %s' % (script_file,func_name,r.status_code,api_call))
            #print api_call, r.json()
            return (False, r.status_code, token3)
        
        elif r.status_code == requests.codes.internal_server_error:
            logging.error('%s:%s: API caused an internal server error. Status Code: %s, API Call: %s' % (script_file,func_name,r.status_code,api_call))
            #print api_call, r.json()
            return (False, r.status_code, token3)
        
        elif r.status_code == requests.codes.bad_request: # 400
            logging.error('%s:%s: Bad request to API. Status Code: %s, API Call: %s' % (script_file,func_name,r.status_code,api_call))
            print api_call, r.json()
            return (False, r.status_code, token3)

        elif r.status_code == requests.codes.not_found: # 404
            logging.debug('%s:%s: Resource not found at API. Status Code: %s, API Call: %s' % (script_file,func_name,r.status_code,api_call))
            #print "ERROR >>>>>>>>>>>>>", api_call, r.json()
            return (False, r.status_code, token3)
        
        elif r.status_code == requests.codes.forbidden: # 403
            logging.error('%s:%s: Forbidden to access API. Status Code: %s, API Call: %s' % (script_file,func_name,r.status_code,api_call))
            print api_call, r.json()
            return (False, r.status_code, token3)
                        
        if r.headers['Content-Type'] in ['application/json'] :
            # return data
            return (True,r.json(),token3)
            
        else:
            logging.error('%s:%s: No valid JSON data retrieved from API' % (script_file,func_name))
            #print "ERROR >>>>>>>>>>>>>", api_call
            #print 'r.request.headers:',r.request.headers
            #print 'r.headers:',r.headers
            #print 'r.content:',r.content
            #exit(1)
            return (False, r.status_code, token3)
    
    except requests.exceptions.ConnectionError as e:
        logging.error('%s:%s: ConnectionError: %s' % (script_file,func_name,e))
        return (False, 503, token3)
