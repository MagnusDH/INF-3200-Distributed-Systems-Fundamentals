#!/bin/bash

rm -r logs

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
        # ssh -f ${current_node} "python3 $PWD/node.py ${current_node}:${current_port}" 

        mkdir -p $PWD/logs
        ssh -f ${current_node} "python3 -u $PWD/node.py ${current_node}:${current_port} > $PWD/logs/${current_node}:${current_port}.log 2>&1 &"

        #Add server to list
        server_list+=("${current_node}:${current_port}")
done


sleep 1
echo -e "Running controller...\n"
python3 controller.py ${server_list[@]}



# echo -e "List of running nodes:\n${server_list[@]}"

# sleep 2
# echo -e "Running api-test.py...\n"
# python3 api-test.py ${server_list[0]}

# sleep 1
# echo -e "Running join_experiment.py...\n"
# python3 join_experiment.py ${server_list[@]}


sleep 2
echo -e "Killing all processes\n"

for (( i=0; i<num_servers; i++ )); do

        node_name=${available_nodes[$(( i % num_servers ))]}

        ssh ${node_name} killall -u $(id -un)
done

echo -e "Killed all processes\n"

