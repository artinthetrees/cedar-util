#!/bin/bash
clear
echo ---------------------------------------------
echo Checking all CEDAR servers
echo ---------------------------------------------
echo

format="| %-27s| %-20s| %-15s| %10s | %-20s|\n"
header="| %-27s| %-9s| %-15s| %10s | %-20s|\n"
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
NORMAL=$(tput sgr0)

function checkStatus {
        if pgrep -f "$2" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
        fi
        printf "$format" $1 $status 'pgrep' ' ' $2
}

function checkHealth {
        ok=1
        lookFor='HTTP/1.1\s200\sOK'
        if curl -I -s http://localhost:$2/healthcheck | grep $lookFor > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
                ok=0
        fi
        printf "$format" $1 $status 'healthCheck' $2 $lookFor
        if ((ok == 0));
        then
                reportError $1 $2
        fi
}

function checkHttpResponse {
        ok=1
        if curl -I -s http://localhost:$2 | grep "$3" > /dev/null 2>&1
        then
                status="${GREEN}Running${NORMAL}"
        else
                status="${RED}Stopped${NORMAL}"
                ok=0
        fi
        printf "$format" $1 $status 'httpResponse' $2 $3
        if ((ok == 0));
        then
                reportError $1 $2
        fi
}

function printLine {
        printf $1'%.0s' {1..93}
        printf '\n'
}

function reportError {
        printLine '.'
        echo -- ERROR IN $1
        echo -- 'http://localhost:'$2
        curl -I http://localhost:$2
        printLine '^'
}

printLine '='

printf "$header" 'Server' 'Status' 'CheckedFor' 'Port' 'Value'

printLine '\x2D'

printf "$header" '--- Microservices ---------'
checkStatus Folder port=9008
checkHealth Group 9109
checkStatus User port=9005
checkStatus Repo port=9002
checkStatus Resource port=9007
checkHealth Schema 9103
checkStatus Template port=9001
checkStatus Terminology port=9004
checkStatus ValueRecommender port=9006
printf "$header" '--- Infrastructure --------'
checkStatus MongoDB mongod
checkHttpResponse Elasticsearch 9200 'HTTP/1.1\s200\sOK'
checkHttpResponse Kibana 5601 'kbn-name:\skibana'
checkHttpResponse NGINX 80 'Server:\snginx'
checkHttpResponse Keycloak 8080 'Server:\sWildFly'
checkHttpResponse Neo4j 7474 'Server:\sJetty'
printf "$header" '--- Development Front End -'
checkHttpResponse Gulp 4200 'HTTP/1.1\s200\sOK'

printLine '='
