#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

configs = {
    "root_path": os.getenv("ROOT_PATH", os.getcwd()),
    "rabbitmq_config": {"username": os.getenv("USERNAME_RM", "jnc"),
                        "password": os.getenv("PASSWORD_RM", "juneng"),
                        "host": os.getenv("HOST_RM", "14.23.57.52"),
                        "port": os.getenv("PORT_RM", 5672),
                        "exchange": os.getenv("EXCHANGE", "sem.server.exchange"),
                        "exchange_type": os.getenv("EXCHANGE_TYPE", "topic"),
                        "queue_name_get": os.getenv("QUEUE_NAME_GET", "record_schedule_data"),
                        "routing_key_get": os.getenv("ROUTING_KEY_GET", "record_schedule_data"),
                        "queue_name_send": os.getenv("QUEUE_NAME_SEND", "record_schedule_data_return"),
                        "routing_key_send": os.getenv("ROUTING_KEY_SEND", "record_schedule_data_return")
                        },
    "redis_config": {"redis_host": os.getenv("REDIS_HOST", "14.23.57.52"),
                     "redis_port": os.getenv("REDIS_PORT", 3682),
                     "redis_pass": os.getenv("REDIS_PASS", "huidian")
                     },
    "database_entity_config": {'host': os.getenv("DATABASE_HOST", "14.23.57.52"),
                               'port': os.getenv("DATABASE_PORT", 6033),
                               'user': os.getenv("DATABASE_USER", 'wemuser'),
                               'passwd': os.getenv("DATABASE_PASSWD", 'wempwd'),
                               'db': os.getenv("DATABASE_DBEMBASE", 'jncqa_cloud_embase'),
                               'charset': os.getenv("DATABASE_CHARSET", 'utf8mb4')
                               },
    'database_meter_config': {'host': os.getenv("DATABASE_HOST", "14.23.57.52"),
                              'port': os.getenv("DATABASE_PORT", 6033),
                              'user': os.getenv("DATABASE_USER", 'wemuser'),
                              'passwd': os.getenv("DATABASE_PASSWD", 'wempwd'),
                              'db': os.getenv("DATABASE_DBSEM", 'jncqa_cloud_sem'),
                              'charset': os.getenv("DATABASE_CHARSET", 'utf8mb4')
                               }
        }
