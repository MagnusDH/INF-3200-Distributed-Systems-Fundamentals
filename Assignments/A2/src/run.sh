#!/bin/bash

#Print a message
echo -e "\n########## Running shell script ##########\n"

#Fetch number of servers that should be started
num_servers=$1 #Fetches command line argument #1

#echo "Number of servers that should be started: ${num_servers}"

#Fetch nodes that are available
# available_nodes=($(/share/ifi/available-nodes.sh))

#Fetch the number of nodes that are available
# num_nodes=${#available_nodes[@]}
#echo "Number of available nodes: ${num_nodes}"

#List of started servers
# JSON_list=()

# for (( i=0; i<num_servers; i++ )); do
#         #Find node to start server on
#         current_node=${available_nodes[$(( i % num_nodes ))]}

#         #Create a unique port number
#         current_port=$(shuf -i 49152-65535 -n1)

#         #Start a background server on current_node with specific port number
#         ssh -f ${current_node} "python3 $PWD/server_app.py ${current_port}"
#         #echo "Started server on ${current_node}:${current_port}"

#         #Add server to JSON-list
#         JSON_list+=("${current_node}:${current_port}")
# done

#Convert JSON_list into string
# json_string="["

# for i in "${!JSON_list[@]}"; do
#     element="${JSON_list[$i]}"
#     json_string+="\"${element}\""

#     #If this is NOT the last element, add comma
#     if [ "$i" -lt $((${#JSON_list[@]} - 1)) ]; then
#         json_string+=", "
#     fi
# done

# #Add closing brack to string
# json_string+="]"
# sleep 1
# echo -e "\nJSON-LIST TO COPY FOR TESTSCRIPT.PY:"
# echo "$json_string"
# echo -e "\n"

#echo -e "\n########## Running testscript.py automaticly in ##########"
#Waiting 2 secons to make sure the servers have started before running testscript.py
#sleep 2
#python3 testscript.py "$json_string"