"""
Environmental Monitoring for cosy

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

# Standard import
import os.path
import sys
import time
import datetime
import json
import spidev


# temp
from random import randint

# Import custom modules
import data.data as data

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, TB_CEVENT, SPOOF_DATA
script_file = "%s: %s" % (now_file,os.path.basename(__file__))

################## Functions ###################################### Functions ###################################### Functions ####################


def ragcalc(level, detail):
    """
    Function to calculate RAG
    
    """
    if detail['red'] > detail['amber'] :
        if level > detail['red'] :
            return 3
        elif level > detail['amber'] :
            return 2
        else:
            return 1
    else:
        if level < detail['red'] :
            return 3
        elif level < detail['amber'] :
            return 2
        else:
            return 1
        

def ReadChannel(spi, channel):
    """
    Function to read SPI data from MCP3008 chip
    Channel must be an integer 0-7
    
    """
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    
    return data
    

def ConvertVolts(data):
    """
    Function to convert data to voltage level,
    rounded to specified number of decimal places.
    
    """
    millivolts = ((data * 3.3) / float(1023))*1000 
    millivolts = int(millivolts)
    
    return millivolts


def ConvertTemp(data, places):
    """
    Function to calculate temperature from
    TMP36 data, rounded to specified number of decimal places.

    """
    # ADC Value
    # (approx)  Temp  Volts
    #    0      -50    0.00
    #   78      -25    0.25
    #  155        0    0.50
    #  233       25    0.75
    #  310       50    1.00
    #  465      100    1.50
    #  775      200    2.50
    # 1023      280    3.30
    
    temp = ((data * 330)/float(1023))-50
    temp = round(temp, places)
    
    return temp
    


def envmon_data(idst, policy_data, default_event):
    """
    Generate environmental monitoring data.
    -- Covered by error handling above function call --
    > idst
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    
## test event script
    
    # json policy data
    policy_data = json.loads(policy_data)
    
    # get seconds interval for event refresh
    pol_int = policy_data['interval']
    
    # get event type ID
    eventcID = default_event['id']
    
    # get last event of type ID
    last_event = data.manage_event(TB_CEVENT, idst['user_id'], method = 'last_event', data = eventcID)
    
    # test if last event present
    if last_event is not None:
        
        # get last event datetime
        last_event_t = datetime.datetime.strptime(last_event['last_date'], '%Y-%m-%d %H:%M:%S.%f')
        
        #print "return with no update if",datetime.datetime.now(),"is less than", last_event_t + datetime.timedelta(seconds=pol_int)
        
        if datetime.datetime.now() < last_event_t + datetime.timedelta(seconds=pol_int) :
            return False

## run environment event script
    logging.debug('%s:%s: Measure Environmental Data for user id: %s control unit id: %s' % (script_file,func_name,idst['user_id'],idst['sysID']))
    
    # start dict
    env_data = {
            'sysID':idst['sysID'],
            'timestamp':{"$date":datetime.datetime.utcnow().isoformat()}, # MongoDB/BSON loadable date format
            'data':{},
            }
    
    env_config = json.loads(default_event['event_action'])
    
    # generate envdata
    if SPOOF_DATA :
        
        # iterate analogue sensors
        for device in env_config['analogue'] :
            
            #print "spi port", device['io']['port']
            #print "spi device", device['io']['device']
            
            # build data
            for name, detail in device['sensors'].iteritems() :
                
                if detail['type'] == 'temp':
                    
                    level = randint(0,1200)
                    
                    env_data['data'][name] = {
                                    'mV':randint(25,55),
                                    'level':level,
                                    'prval':randint(20,50),
                                    'prunit':'degC',
                                    'type':detail['type'],
                                    'rag':ragcalc(level,detail),
                                    }
                
                elif detail['type'] == 'light':
                    
                    level = randint(0,1200)
                    
                    env_data['data'][name] = {
                                    'mV':randint(25,55),
                                    'level':level,
                                    'prval':randint(20,50),
                                    'prunit':'level',
                                    'type':detail['type'],
                                    'rag':ragcalc(level,detail),
                                    }
                    
                elif detail['type'] == 'moisture':
                    
                    level = randint(0,1200)
                    
                    env_data['data'][name] = {
                                    'mV':randint(25,55),
                                    'level':level,
                                    'prval':randint(20,50),
                                    'prunit':'level',
                                    'type':detail['type'],
                                    'rag':ragcalc(level,detail),
                                    }
                
                else:
                    env_data['data'][name] = {
                                    'mV':0,
                                    'level':0,
                                    'prval':0,
                                    'prunit':None,
                                    'type':'unknown',
                                    'rag':0,
                                    }
    
    # Get data from sensors
    else: 
        
        # iterate analogue sensors
        for device in env_config['analogue'] :
            
            #print "spi port", device['io']['port']
            #print "spi device", device['io']['device']
            
            # Open SPI bus
            spi = spidev.SpiDev()
            spi.open(device['io']['port'],device['io']['device'])
            
            # build data
            for name, detail in device['sensors'].iteritems() :
                
                if detail['type'] == 'temp':
                    
                    level = ReadChannel(spi,detail['channel'])
                    
                    env_data['data'][name] = {
                        'mV':ConvertVolts(level),
                        'level':level,
                        'prval':ConvertTemp(level,2),
                        'prunit':'degC',
                        'type':detail['type'],
                        'rag':ragcalc(level,detail),
                        }
                
                elif detail['type'] == 'light':
                    
                    level = ReadChannel(spi,detail['channel'])
                    
                    env_data['data'][name] = {
                        'mV':ConvertVolts(level),
                        'level':level,
                        'prval':level,
                        'prunit':'level',
                        'type':detail['type'],
                        'rag':ragcalc(level,detail),
                        }
                    
                elif detail['type'] == 'moisture':
                    
                    level = ReadChannel(spi,detail['channel'])
                    
                    env_data['data'][name] = {
                        'mV':ConvertVolts(level),
                        'level':level,
                        'prval':level,
                        'prunit':'level',
                        'type':detail['type'],
                        'rag':ragcalc(level,detail),
                        }
                
                else:
                    env_data['data'][name] = {
                        'mV':0,
                        'level':0,
                        'prval':0,
                        'prunit':None,
                        'type':'unknown',
                        'rag':0,
                        }
        
            # close spi bus
            spi.close()
    
## compile event
    
    # data to json
    data_json = json.dumps(env_data)
    
    # starting conditions
    parent_event = None
    
    # target up events
    if default_event['target_up'] is not None :
        
        # data to event
        event = {
                'control_sys':idst['sysID'],
                'event_config':eventcID,
                'parent_event':parent_event,
                'source':idst['system_type'],
                'target':default_event['target_up'],
                'data':data_json,
                'transactionID':None,
                'priority':default_event['base_priority'],
                'link_complete_req':default_event['complete_req_up'],
                }
        
        # log to database
        inserted_id = data.manage_event(TB_CEVENT, idst['user_id'], data = event)

        # set up as parent to link to target down event
        parent_event = inserted_id

    # target down events
    if default_event['target_down'] is not None :
        
        # data to event
        event = {
                'control_sys':idst['sysID'],
                'event_config':eventcID,
                'parent_event':parent_event,
                'source':idst['system_type'],
                'target':default_event['target_down'],
                'data':data_json,
                'transactionID':None,
                'priority':default_event['base_priority'],
                'link_complete_req':default_event['complete_req_down'],
                }
        
        # log to database
        inserted_id = data.manage_event(TB_CEVENT, idst['user_id'], data = event)
    
    return True
    
    




################## Script ###################################### Script ###################################### Script ####################




