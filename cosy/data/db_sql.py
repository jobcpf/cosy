"""
Module SQL Data Structures

@Author: 
@Date: 

"""
################## Variables #################################### Variables #################################### Variables ##################

from global_config import DB_API, DB_DATA

################## DB Structure #################################### DB Structure #################################### DB Structure ##################

DATABASES = {
    DB_API : {
        'user':{
            'sort':0,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'sfields':{
                'user':'TEXT NOT NULL',
                'passwd':'TEXT NOT NULL',
                'client_id':'TEXT NOT NULL',
                'client_secret':'TEXT NOT NULL',
                'create_date':'TIMESTAMP',
            },
            'commands':{
                'CREATE UNIQUE INDEX':'user01 ON user (user)',
            },
        },
        'auth':{
            'sort':1,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'access_token':'TEXT NOT NULL',
                'token_type':'TEXT NOT NULL',
                'expires_in':'INTEGER',
                'refresh_token':'TEXT',
                'scope':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            },
            'constraints':{
                'FOREIGN KEY':'(user_id) REFERENCES user (id)',
            }
        },
        'apiaccessconfig':{
            'sort':1,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'api_version':'TEXT NOT NULL',
                'api_url':'TEXT NOT NULL',
                'refresh':'INTEGER',
                'init':'INTEGER DEFAULT 0',
                'cs_required':'INTEGER DEFAULT 0',
                'mt_required':'INTEGER DEFAULT 0',
                'tr_required':'INTEGER DEFAULT 0',
                'description':'TEXT DEFAULT NULL',
                'table_name':'TEXT DEFAULT NULL',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            },
            'constraints':{
                'FOREIGN KEY':'(user_id) REFERENCES user (id)',
            }
        },
    },
    DB_DATA : {
        'controlunit':{
            'sort':0,
            'pk':{
                'cuID':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'sysID':'BIGINT UNIQUE NOT NULL',
                'status':'TEXT',
                'status_bool':'INTEGER NOT NULL',
                'cu_identifier':'TEXT NOT NULL',
                'create_date':'TIMESTAMP',
                'system_type':'INTEGER',
                'parent_sysID':'INTEGER',
                'details':'TEXT',
                'URI':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
                'self_bool':'INTEGER DEFAULT 0',
                'slave_bool':'INTEGER DEFAULT 0',
                'parent_bool':'INTEGER DEFAULT 0',
                'last_config':'TIMESTAMP',
            }
        },
        'systemregister':{
            'sort':0,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'name':'TEXT NOT NULL',
                'system_description':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            }
        },
        'eventtypes':{
            'sort':1,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'name':'TEXT NOT NULL',
                'event_description':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            }
        },
        'controlpolicy':{
            'sort':1,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'default_system':'INTEGER',
                'default_event':'INTEGER',
                'name':'TEXT',
                'policy_data':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            },
            'constraints':{
                'FOREIGN KEY (default_system)':'REFERENCES systemregister (id)',
            }
        },
        'controleventconfig':{
            'sort':2,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'target_up':'INTEGER',
                'target_down':'INTEGER',
                'event_type':'INTEGER NOT NULL',
                'name':'TEXT',
                'event_action':'TEXT',
                'base_priority':'INTEGER',
                'complete_req_up':'INTEGER DEFAULT 0',
                'complete_req_down':'INTEGER DEFAULT 0',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            },
            'constraints':{
                'FOREIGN KEY (target_up)':'REFERENCES systemregister (id)',
                'FOREIGN KEY (target_down)':'REFERENCES systemregister (id)',
                'FOREIGN KEY (event_type)':'REFERENCES eventtypes (id)',
            }
        },
        'controlevent':{
            'sort':3,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'control_sys':'INTEGER',
                'event_config':'INTEGER',
                'parent_event':'INTEGER',
                'source':'INTEGER',
                'target':'INTEGER',
                'data':'TEXT',
                'transactionID':'INTEGER',
                'priority':'INTEGER',
                'complete':'INTEGER DEFAULT 0',
                'link_complete_req':'INTEGER DEFAULT 0',
                'link_confirmed':'INTEGER DEFAULT 0',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            },
            'constraints':{
                'FOREIGN KEY (control_sys)':'REFERENCES controlunit (sysID)',
                'FOREIGN KEY (event_config)':'REFERENCES controleventconfig (id)',
                'FOREIGN KEY (parent_event)':'REFERENCES controlevent (id)',
                'FOREIGN KEY (source)':'REFERENCES systemregister (id)',
                'FOREIGN KEY (target)':'REFERENCES systemregister (id)',
            },
            'commands':{
                'CREATE UNIQUE INDEX transactionID_01':'ON controlevent (control_sys,transactionID)',
            }
        },
        'commsqueue':{
            'sort':1,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'control_sys':'INTEGER NOT NULL',
                'meter':'INTEGER',
                'data':'TEXT',
                'transactionID':'INTEGER NOT NULL',
                'source':'INTEGER',
                'target':'INTEGER',
                'priority':'INTEGER',
                'complete_req':'INTEGER DEFAULT 0',
                'complete':'INTEGER DEFAULT 0',
                'URI':'TEXT',
            },
            'sfields':{
                'comm_sent':'INTEGER DEFAULT 0',
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            },
            'constraints':{
                'FOREIGN KEY (control_sys)':'REFERENCES controlunit (sysID)',
                'FOREIGN KEY (source)':'REFERENCES systemregister (id)',
                'FOREIGN KEY (target)':'REFERENCES systemregister (id)',
            },
            'commands':{
                'CREATE UNIQUE INDEX transactionID_02':'ON commsqueue (control_sys,transactionID)',
            },
        }
    }
}
