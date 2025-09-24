#!/bin/bash

#Print a message
# echo -e "\n########## Running shell script ##########\n"

#Fetch number of servers that should be started
num_servers=$1 #Fetches command line argument #1

#Fetch nodes that are available
available_nodes=($(/share/ifi/available-nodes.sh))

#Start each server and add their IP addresses to a list
echo -e "Starting servers...\n"
server_list=()
for (( i=0; i<num_servers; i++ )); do
        #Find node to start server on
        current_node=${available_nodes[$(( i % num_servers ))]}

        #Create a unique port number for this server
        current_port=$(shuf -i 49152-65535 -n1)

        #ssh into each node and start a background server on that node with a specific port number
        # ssh -f ${current_node} "python3 $PWD/server.py ${current_port}" 
        ssh -f ${current_node} "python3 $PWD/server.py ${current_port} > ${current_node}:${current_port}.log" 
        # ssh -f ${current_node} "cd $(pwd) && nohup python3 -u server.py ${current_port} > server-${current_node}-${current_port}.log 2>&1 &"

        #Add server to list
        server_list+=("${current_node}:${current_port}")
done

#Run a python file that initializes the ring with IDs and finger tables
sleep 2
echo -e "Initializing ring...\n"
python3 initialize_ring.py ${server_list[@]}

#Run client-py to simulate a user of the system
sleep 2
echo -e "Running client...\n"
python3 client.py ${server_list[0]}

# echo -e "Running chord-tester.py...\n"
# sleep 2
# python3 chord-tester.py ${server_list[0]}
