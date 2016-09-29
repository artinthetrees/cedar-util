#!/bin/bash
clear
echo ---------------------------------------------
echo Checking all CEDAR servers
echo ---------------------------------------------
echo

format="CEDAR %-20s:%-10s (%-30s)\n"
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)

function checkStatus {
        if pgrep -f "$2"> /dev/null
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
        fi
        printf "$format" $1 $status $2
}


echo ---
checkStatus Folder port=9008
checkStatus Permission port=9009
checkStatus User port=9005
checkStatus Repo port=9002
checkStatus Resource port=9007
checkStatus Schema port=9003
checkStatus Template port=9001
checkStatus Terminology port=9004
checkStatus ValueRecommender port=9006
echo ---
checkStatus MongoDB mongod
checkStatus Elasticsearch org.elasticsearch.bootstrap
checkStatus Kibana kibana
checkStatus NGINX nginx:
checkStatus Keycloak keycloak/standalone
checkStatus Neo4j Neo4j
echo ---
checkStatus Gulp gulp
