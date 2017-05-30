#!/usr/bin/python
"""
Call Daemon for cosy on Pi

@Author: 
@Date: 

"""
################## Packages #################################### Packages #################################### Variables ##################

import sys
sys.path.append("/home/pi/cosy/cosy") # append python project directory root

# Standard import
import time
import os.path

# Import custom modules
from cosy_daemon import Daemon
import cosy_run as crun

################## Variables #################################### Variables #################################### Variables ##################

from global_config import logging, now_file, BASE_SLEEP, PID_FILE
script_file = "%s: %s" % (now_file,os.path.basename(__file__))
func_name = 'cosy_daemon'

################## Classes ###################################### Classes ###################################### Classes ####################

class CosyDaemon(Daemon):
    """
    Subclass Daemon class to run cosy scripts.
    
    """
    
    def run(self):
        
        idst = None
        token3 = None
        pol_sleep = BASE_SLEEP
        
        while True:
            # logging
            now_file = time.strftime('%Y%m%d_%H%M%S')
            logging.debug('%s:%s: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DAEMON (%s) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<</n' % (script_file,func_name,now_file))
            #print '%s: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DAEMON ( %s) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' % (func_name,now_file)
            
            
            # call script run script
            rbool, idst, token3, pol_sleep = crun.cosy_run(idst, token3)
            
            # delay/re-run
            time.sleep(pol_sleep)


################## Scripts ###################################### Scripts ###################################### Scripts ####################


if __name__ == "__main__":
    daemon = CosyDaemon(PID_FILE)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            #logging.debug('%s:%s: Starting COSY Daemon' % (script_file,func_name))
            daemon.start()
            
        elif 'stop' == sys.argv[1]:
            #logging.debug('%s:%s: Stopping COSY Daemon' % (script_file,func_name))
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            #logging.debug('%s:%s: Restarting COSY Daemon' % (script_file,func_name))
            daemon.restart()
            
        elif 'test' == sys.argv[1]:
            #logging.debug('%s:%s: Starting COSY Daemon in TEST mode (foreground)' % (script_file,func_name))
            daemon.run()
            
        else:
            #logging.error('%s:%s: Unknown daemon command for COSY' % (script_file,func_name))
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|test)" % sys.argv[0]
        sys.exit(2)


