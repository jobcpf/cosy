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
from datetime import datetime
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
    

def ConvertVolts(data, places):
    """
    Function to convert data to voltage level,
    rounded to specified number of decimal places.
    
    """
    volts = (data * 3.3) / float(1023)
    volts = round(volts, places)
    
    return volts


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



def envmon_data(id6):
    """
    Generate environmental monitoring data.
    > id6
    < True, False
    
    """
    func_name = sys._getframe().f_code.co_name # Defines name of function for logging
    logging.debug('%s:%s: Measure Environmental Data for user id: %s control unit id: %s' % (script_file,func_name,id6['user_id'],id6['sysID']))
    
    
    if SPOOF_DATA :
    
        # generate envdata
        env_data = {
            'temp1':randint(10,50),
            'temp2':randint(10,50),
            'temp3':randint(10,50),
            'temp4':randint(10,50),
            'temp5':randint(10,50),
        }
    
    else: 
        # Open SPI bus
        spi = spidev.SpiDev()
        spi.open(0,0)
        
        # Define sensor channels
        light_channel = 0
        light2_channel = 7
        temp_channel  = 1
        temp2_channel  = 2
        moisture_channel = 3
        
        # Read the light sensor data
        light_level = ReadChannel(spi,light_channel)
        light_volts = ConvertVolts(light_level,2)
        
        # Read the light sensor data
        light2_level = ReadChannel(spi,light2_channel)
        light2_volts = ConvertVolts(light2_level,2)
        
        # Read the moisture sensor data
        moisture_level = ReadChannel(spi,moisture_channel)
        moisture_volts = ConvertVolts(moisture_level,2)
        
        # Read the temperature sensor data
        temp_level = ReadChannel(spi,temp_channel)
        temp_volts = ConvertVolts(temp_level,2)
        temp       = ConvertTemp(temp_level,2)
        
        # Read the temperature sensor data
        temp2_level = ReadChannel(spi,temp2_channel)
        temp2_volts = ConvertVolts(temp2_level,2)
        temp2       = ConvertTemp(temp2_level,2)
        
        nowtime     = datetime.now()
        
        env_data = {'time':str(nowtime),
                    'temp1':temp,
                    'temp2':temp2,
                    'light1':light_level,
                    'light2':light2_level,
                    'moisture':moisture_level,
                }
    
    
    # data to json
    data_json = json.dumps(env_data)
    
    # data to event
    event = {
            'control_sys':id6['sysID'],
            'event_config':'1',
            'parent_event':None,
            'source':id6['system_type'],
            'target':13,
            'data':data_json,
            'transactionID':None,
            'priority':1,
            'link_complete_req':1,

    }
    
    # log to database
    data_inserted = data.insert_data(id6['user_id'], TB_CEVENT, event)
    
    return True
    
    




################## Script ###################################### Script ###################################### Script ####################




