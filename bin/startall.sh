#!/bin/bash
clear
echo --------------------------------------------------------------------------------
echo Starting Dropwizard enabled CEDAR microservices
echo - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

shopt -s expand_aliases
source $CEDAR_HOME/cedar-util/bin/profile_include.sh

startworkspace
startgroup
startmessaging
startrepo
startresource
startschema
starttemplate
startterminology
startuser
startvaluerecommender
startsubmission
startworker
