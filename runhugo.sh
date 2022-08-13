#!/bin/bash

# assume hugo in the same directory as the runhugo.sh
CMD=`echo $0 | sed -e "s/.*\/\(.*\)$/\1/g"`
HOME=`echo $0 | sed -e "s/\(.*\)${CMD}/\1/g"`
PUBLICIP=`curl http://checkip.amazonaws.com`
(cd $HOME && sudo ./hugo server -w --baseUrl=http://$PUBLICIP --bind=0.0.0.0 -p 80)


