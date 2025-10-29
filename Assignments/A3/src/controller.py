import sys
import requests
import time

if len(sys.argv) < 1:
    print("controller.py: missing command line argument")
    sys.exit(1)

#Fetch node from command line argument
list_nodes = sys.argv[1:]

#Make node_i contact node_0
try:
    for i in range(16):
        if(i != 0):
            print(f"Node {i} joining circle")
            response = requests.post(f"http://{list_nodes[i]}/join?nprime={list_nodes[0]}")

            # time.sleep(1)
    
    time.sleep(10)

    # #Crash a node
    # for i in range(3):
    #     print("Crashing a node...")
    #     requests.post(f"http://{list_nodes[i]}/sim-crash")
    #     time.sleep(2)

    #Make a node leave the ring voluntarily
    # time.sleep(8)
    # print("Node leaving circle...")
    # requests.post(f"http://{list_nodes[2]}/leave")

    # print("Node rejoining circle...")
    # requests.post(f"http://{list_nodes[2]}/sim-recover")
    # time.sleep(5)

    #Add and retrieve values from the circle
    # for i in range(3):
    #     print("Adding value to circle...")
    #     requests.put(f"http://{list_nodes[i]}/storage/bais{i}", data=f"bais{i}")
    #     time.sleep(1)
    
    # for i in range(3):
    #     print("Retreiving value from circle...")
    #     response = requests.get(f"http://{list_nodes[i]}/storage/bais{i}")
    #     print("Got response: ", response.text)
    #     time.sleep(1)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
