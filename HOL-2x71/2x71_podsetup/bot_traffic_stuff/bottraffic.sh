#!/bin/bash
/usr/bin/docker run -it --rm \
    -e "LOCUST_LOCUSTFILE=dvwa_traffic_spoof_true_clientip.py" \
    -e "LOCUST_HOST=https://172.16.130.12" -e "LOCUST_HEADLESS=true" \
    -e "LOCUST_USERS=20" -e "LOCUST_SPAWN_RATE=1" --pull=always \
    projects.registry.vmware.com/nsx_alb/locust_demotraffic:v9