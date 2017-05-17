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
                'created_at':'TIMESTAMP',
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
                'created_at':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            },
            'constraints':{
                'FOREIGN KEY':'(user_id) REFERENCES user (id)',
            }
        },
        'apiaccessconfig':{
            'sort':2,
            'pk':{
                'id':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'api_version':'TEXT NOT NULL',
                'api_url':'TEXT NOT NULL',
                'refresh':'INTEGER',
                'init':'INTEGER DEFAULT 0',
                'cs_required':'INTEGER DEFAULT 0',
                'mt_required':'INTEGER DEFAULT 0',
                'tr_required':'INTEGER DEFAULT 0',
                'description':'TEXT DEFAULT NULL',
            },
            'sfields':{
                'created_at':'TIMESTAMP',
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
            'pk':{
                'cuID':'INTEGER PRIMARY KEY',
            },
            'vfields':{
                'status':'TEXT',
                'status_bool':'INTEGER NOT NULL',
                'cu_identifier':'TEXT NOT NULL',
                'create_date':'TIMESTAMP',
            },
            'sfields':{
                'last_date':'TIMESTAMP',
                'user_id':'INTEGER NOT NULL',
            }
        },
    }
}

db_api_sql = [
        """CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            user TEXT unique NOT NULL,
            passwd TEXT NOT NULL,
            control_unit INTEGER,
            created_at TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS auth (
            id INTEGER PRIMARY KEY,
            access_token TEXT NOT NULL,
            token_type TEXT NOT NULL,
            expires_in INTEGER,
            refresh_token TEXT,
            scope TEXT,
            created_at TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );""",
        """CREATE TABLE IF NOT EXISTS apiaccessconfig (
            apiid INTEGER PRIMARY KEY,
            api_version TEXT NOT NULL,
            api_url TEXT NOT NULL,
            description TEXT,
            refresh INTEGER,
            init INTEGER DEFAULT 0,
            cs_required INTEGER DEFAULT 0,
            mt_required INTEGER DEFAULT 0,
            tr_required INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );""",
]

db_data_sql = [
        """CREATE TABLE `envmon_controlevent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `complete` tinyint(1) NOT NULL,
  `create_date` datetime(6) NOT NULL,
  `last_date` datetime(6) NOT NULL,
  `control_unit_id` int(11) DEFAULT NULL,
  `event_config_id` int(11) DEFAULT NULL,
  `transactionID` bigint(20) DEFAULT NULL,
  `event_data` varchar(200) DEFAULT NULL,
  `link_complete` tinyint(1) NOT NULL,
  `parent_event_id` int(11) DEFAULT NULL,
  `target_id` int(11) DEFAULT NULL,
  `link_complete_req` tinyint(1) NOT NULL,
  `link_confirmed` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `envmon_controlevent_control_unit_id_814425e7_fk_envmon_co` (`control_unit_id`),
  KEY `envmon_controlevent_event_config_id_ac018124_fk_envmon_co` (`event_config_id`),
  KEY `envmon_controlevent_transactionID_453ce755` (`transactionID`),
  KEY `envmon_controlevent_parent_event_id_2ebf0dbe_fk_envmon_co` (`parent_event_id`),
  KEY `envmon_controlevent_source_id_859e2f82` (`source_id`),
  KEY `envmon_controlevent_target_id_52a1ab8b` (`target_id`),
  CONSTRAINT `envmon_controlevent_control_unit_id_814425e7_fk_envmon_co` FOREIGN KEY (`control_unit_id`) REFERENCES `envmon_controlunit` (`cuID`),
  CONSTRAINT `envmon_controlevent_event_config_id_ac018124_fk_envmon_co` FOREIGN KEY (`event_config_id`) REFERENCES `envmon_controleventconfig` (`id`),
  CONSTRAINT `envmon_controlevent_parent_event_id_2ebf0dbe_fk_envmon_co` FOREIGN KEY (`parent_event_id`) REFERENCES `envmon_controlevent` (`id`),
  CONSTRAINT `envmon_controlevent_source_id_859e2f82_fk_envmon_sy` FOREIGN KEY (`source_id`) REFERENCES `envmon_systemregister` (`id`),
  CONSTRAINT `envmon_controlevent_target_id_52a1ab8b_fk_envmon_sy` FOREIGN KEY (`target_id`) REFERENCES `envmon_systemregister` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8
        );""",
        """CREATE TABLE IF NOT EXISTS auth (
            id INTEGER PRIMARY KEY,
            access_token TEXT NOT NULL,
            token_type TEXT NOT NULL,
            expires_in INTEGER,
            refresh_token TEXT,
            scope TEXT,
            created_at TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );""",
        """CREATE TABLE IF NOT EXISTS apiaccessconfig (
            apiid INTEGER PRIMARY KEY,
            api_version TEXT NOT NULL,
            api_url TEXT NOT NULL,
            description TEXT,
            refresh INTEGER,
            init INTEGER DEFAULT 0,
            cs_required INTEGER DEFAULT 0,
            mt_required INTEGER DEFAULT 0,
            tr_required INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        );""",
]