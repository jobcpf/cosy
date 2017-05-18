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
            'vfields':{
                'user':'TEXT unique NOT NULL',
                'passwd':'TEXT NOT NULL',
                'control_unit':'INTEGER',
            },
            'sfields':{
                'create_date':'TIMESTAMP',
            }
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
                'FOREIGN KEY':' (user_id) REFERENCES user (id)',
            }
        },
        'commsqueue':{
            'sort':0,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'control_unit':'INTEGER NOT NULL',
                'meter':'INTEGER',
                'comm_data':'TEXT',
                'transactionID':'INTEGER',
                'source':'INTEGER',
                'target':'INTEGER',
                'priority':'INTEGER',
                'comm_sent':'INTEGER DEFAULT 0',
                'comm_complete_req':'INTEGER DEFAULT 0',
                'comm_complete':'INTEGER DEFAULT 0',
                'URI':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            },
            'constraints':{
                'FOREIGN KEY':' (user_id) REFERENCES user (id)',
            }
        }
    },
    DB_DATA : {
        'controlunit':{
            'sort':0,
            'vfields':{
                'cuID':'INTEGER PRIMARY KEY',
                'status':'TEXT',
                'status_bool':'INTEGER NOT NULL',
                'cu_identifier':'TEXT NOT NULL',
                'create_date':'TIMESTAMP',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
                'self':'INTEGER DEFAULT 0',
                'slave':'INTEGER DEFAULT 0',
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
                'name':'TEXT',
                'policy_data':'TEXT',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            },
            'constraints':{
                'FOREIGN KEY':' (default_system) REFERENCES systemregister (id)',
            }
        },
        'controleventconfig':{
            'sort':2,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'event_owner':'INTEGER',
                'target_up':'INTEGER',
                'target_down':'INTEGER',
                'event_type':'INTEGER',
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
                'FOREIGN KEY':' (event_owner) REFERENCES systemregister (id)',
                'FOREIGN KEY':' (target_up) REFERENCES systemregister (id)',
                'FOREIGN KEY':' (target_down) REFERENCES systemregister (id)',
                'FOREIGN KEY':' (event_type) REFERENCES eventtypes (id)',
            }
        },
        'controlevent':{
            'sort':3,
            'vfields':{
                'id':'INTEGER PRIMARY KEY',
                'control_unit':'INTEGER',
                'event_config':'INTEGER',
                'parent_event':'INTEGER',
                'source':'INTEGER',
                'target':'INTEGER',
                'event_data':'TEXT',
                'transactionID':'INTEGER',
                'priority':'INTEGER',
                'link_confirmed':'INTEGER DEFAULT 0',
                'link_complete_req':'INTEGER DEFAULT 0',
                'link_complete':'INTEGER DEFAULT 0',
                'complete':'INTEGER DEFAULT 0',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL'
            },
            'constraints':{
                'FOREIGN KEY':' (control_unit) REFERENCES controlunit (id)',
                'FOREIGN KEY':' (event_config) REFERENCES controleventconfig (id)',
                'FOREIGN KEY':' (parent_event) REFERENCES controlevent (id)',
                'FOREIGN KEY':' (source) REFERENCES systemregister (id)',
                'FOREIGN KEY':' (target) REFERENCES systemregister (id)',
            }
        },
    }
}
