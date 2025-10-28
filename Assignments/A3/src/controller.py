import sys
import requests
import time

if len(sys.argv) < 1:
    print("controller.py: missing command line argument")
    sys.exit(1)

#Fetch node from command line argument
list_nodes = sys.argv[1:]

#Make node_0 contact node_1
try:
    for i in range(4):
        if(i != 0):
            print(f"Node {i} joining circle")
            response = requests.post(f"http://{list_nodes[i]}/join?nprime={list_nodes[0]}")

            time.sleep(1)
    
    # #Crash a node
    # time.sleep(10)
    # print("Crashing a node...")
    # requests.post(f"http://{list_nodes[1]}/sim-crash")

    #Make a node leave the ring voluntarily
    time.sleep(8)
    print("Node leaving circle...")
    requests.post(f"http://{list_nodes[2]}/leave")

    time.sleep(8)
    print("Node rejoining circle...")
    requests.post(f"http://{list_nodes[2]}/sim-recover")
    time.sleep(5)


except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
