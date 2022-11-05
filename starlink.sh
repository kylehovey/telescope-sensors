#!/bin/bash

python ../starlink-grpc-tools/dish_grpc_mqtt.py --hostname 192.168.1.20 --port 1883 -t 10 status obstruction_detail alert_detail ping_drop ping_run_length ping_latency ping_loaded_latency usage
