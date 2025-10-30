import sys
import requests
import time


def is_network_stable(start_node):
    print("IS_NETWORK_STABLE()")

    #Create set that each node can add their ID to
    visited = []

    try:
        #Send a request from the start node
        message_payload = {
            "start_node": list_nodes[0],
            "visited": visited,
            "num_hops": 0,
            "first": True}
        response = requests.post(f"http://{list_nodes[0]}/check_stable_network", json=message_payload)

        #Unpack response
        received_data = response.json()
        start_node = received_data["start_node"]
        visited = received_data["visited"]
        num_hops = received_data["num_hops"]
        first = received_data["first"]

        #If visited list is the length of list_nodes, then all nodes have been visited and ring is stable
        if(len(visited) == len(list_nodes)):
            print("Number of hops made: ", num_hops)
            return True
        
        else:
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"Could not contact node to check if network is stable: {e}")


#Makes n_nodes join the ring via node_0
def create_ring(n_nodes):
    #Nodes enter the ring
    for i in range(n_nodes):
        if(i != 0):
            try:
                print(f"Node {i} joining circle")
                response = requests.post(f"http://{list_nodes[i]}/join?nprime={list_nodes[0]}")
            
            except requests.exceptions.RequestException as e:
                print(f"Node {i} failed to join: {e}")
                sys.exit(1)     


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("controller.py: missing command line argument")
        sys.exit(1)

    #Fetch node from command line argument
    list_nodes = sys.argv[1:-1]

    #Last command argument is the number of nodes to start
    NUMBER_OF_NODES = int(sys.argv[-1])

    #Start timer
    start_time = time.time()


    #Make nodes join ring
    create_ring(NUMBER_OF_NODES)

    #Check if ring is stable
    ring_stable = False
    counter = 0
    while ring_stable == False:
        counter += 1
        result = is_network_stable(list_nodes[0])
        if result == True:
            print("RING IS STABLE")
            ring_stable = True
            break
        else:
            print("RING NOT STABLE")
            if(counter == 5):
                break
        
        time.sleep(3)

    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time to grow network to {NUMBER_OF_NODES} nodes: {duration:.2f} seconds")








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

