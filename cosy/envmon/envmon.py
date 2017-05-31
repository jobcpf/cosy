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
    env_data = {}
    
    env_config = json.loads(default_event['event_action'])
    
    # generate envdata
    if SPOOF_DATA :
        
        # iterate analogue sensors
        for device in env_config['analogue'] :
            
            for key, config in device.iteritems() :
                
                #print "spi port", config['io']['port']
                #print "spi device", config['io']['device']
                
                # build data
                for name, detail in config['sensors'].iteritems() :
                    
                    if detail['type'] == 'temp':
                        
                        env_data[name] = {
                                        'mV':randint(25,55),
                                        'level':randint(0,1200),
                                        'degC':randint(20,50),
                                        }
                    
                    elif detail['type'] == 'light':
                        
                        env_data[name] = {
                                        'mV':randint(25,55),
                                        'level':randint(0,1200),
                                        }
                        
                    elif detail['type'] == 'moisture':
                        
                        env_data[name] = {
                                        'mV':randint(25,55),
                                        'level':randint(0,1200),
                                        }
                    
                    else:
                        env_data[name] = {
                                        'V':0,
                                        'level':0,
                                        'error':'unknown type'
                                        }
    
    # Get data from sensors
    else: 
        
        # iterate analogue sensors
        for device in env_config['analogue'] :
            
            for key, config in device.iteritems() :
                
                #print "spi port", config['io']['port']
                #print "spi device", config['io']['device']
                
                # Open SPI bus
                spi = spidev.SpiDev()
                spi.open(config['io']['port'],config['io']['device'])
                
                # build data
                for name, detail in config['sensors'].iteritems() :
                    
                    if detail['type'] == 'temp':
                        
                        level = ReadChannel(spi,detail['channel'])
                        
                        env_data[name] = {
                            'mV':ConvertVolts(level),
                            'level':level,
                            'degC':ConvertTemp(level,2),
                            }
                    
                    elif detail['type'] == 'light':
                        
                        level = ReadChannel(spi,detail['channel'])
                        
                        env_data[name] = {
                            'mV':ConvertVolts(level),
                            'level':level,
                            }
                        
                    elif detail['type'] == 'moisture':
                        
                        level = ReadChannel(spi,detail['channel'])
                        
                        env_data[name] = {
                            'mV':ConvertVolts(level),
                            'level':level,
                            }
                    
                    else:
                        env_data[name] = {
                            'mV':0,
                            'level':0,
                            'error':'unknown type'
                            }
        
                # close spi bus
                spi.close()
    
## compile event
    
    # append meta data
    env_data['meta'] = {
             'sysID':idst['sysID'],
             'timestamp':str(datetime.datetime.now()),
            }
    
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




