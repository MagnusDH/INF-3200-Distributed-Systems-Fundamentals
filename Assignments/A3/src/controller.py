import sys
import requests
import time


def is_network_stable(start_node_IP, num_nodes):
    # print("IS_NETWORK_STABLE()")

    #Create set that each node can add their ID to
    visited = []

    try:
        #Send a request from the start node
        message_payload = {
            "start_node": start_node_IP,
            "visited": visited,
            "num_hops": 0,
            "first": True}
        response = requests.post(f"http://{start_node_IP}/check_stable_network", json=message_payload)

        if(response.status_code == 200):
            #Unpack response
            received_data = response.json()
            start_node = received_data["start_node"]
            visited = received_data["visited"]
            num_hops = received_data["num_hops"]
            first = received_data["first"]

            #If visited list is the length of list_nodes, then all nodes have been visited and ring is stable
            if(len(visited) == num_nodes):
                return True
            
            else:
                return False
        else:
            print("Got response that was not '200'. Something wrong happened")
            sys.exit(1)
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"Could not contact node to check if network is stable: {e}")
        sys.exit(1)   



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


#Makes n_nodes leave the ring
def shrink_ring(n_nodes):
    #Nodes leave the ring
    for i in range(n_nodes):
        try:
            print(f"Node {i} leaving circle")
            requests.post(f"http://{list_nodes[i]}/leave")
            
        except requests.exceptions.RequestException as e:
            print(f"Node {i} failed to leave: {e}")
            sys.exit(1)   


#Crashes n_nodes in the ring
def crash_nodes(n_nodes):
    #Crash nodes
    for i in range(n_nodes):
        try:
            print(f"Crashing node...")
            requests.post(f"http://{list_nodes[i]}/sim-crash")
            
        except requests.exceptions.RequestException as e:
            print(f"Node {i} failed to crash: {e}")
            sys.exit(1)   

        
        time.sleep(1)



if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("controller.py: missing command line argument")
        sys.exit(1)

    #Fetch node from command line argument
    list_nodes = sys.argv[1:-1]

    #Last command argument is the number of nodes to start
    NUMBER_OF_NODES = int(sys.argv[-1])


    ############ grow network ############  
    #Start timer
    start_grow_time = time.time()

    #Make nodes join ring
    create_ring(NUMBER_OF_NODES)

    #Check if ring is stable
    ring_stable = False
    counter = 0
    while ring_stable == False:
        counter += 1
        result = is_network_stable(list_nodes[0], NUMBER_OF_NODES)
        if result == True:
            print("RING IS STABLE")
            ring_stable = True
            break
        else:
            print("RING NOT STABLE", counter)
            if(counter == 50):
                sys.exit(1)
                break
        
        time.sleep(2)

    
    end_grow_time = time.time()
    grow_duration = end_grow_time - start_grow_time
    print(f"Time to grow network to {NUMBER_OF_NODES} nodes: {grow_duration:.2f} seconds")


    # ############ Shrink network ############
    # #Start timer
    # start_shrink_time = time.time()

    # #Send leave-calls to nodes
    # shrink_ring(int(NUMBER_OF_NODES/2))

    # #Check if ring is stable
    # ring_stable = False
    # counter = 0
    # while ring_stable == False:
    #     counter += 1
    #     result = is_network_stable(list_nodes[-1], NUMBER_OF_NODES/2)
    #     if result == True:
    #         print("RING IS STABLE", counter)
    #         ring_stable = True
    #         break
    #     else:
    #         print("RING NOT STABLE")
    #         if(counter == 30):
    #             break
        
    #     time.sleep(2)


    # end_shrink_time = time.time()
    # shrink_duration = end_shrink_time - start_shrink_time
    # print(f"Time to become stable after {NUMBER_OF_NODES/2} leaves: {shrink_duration:.2f} seconds")



    ############ Crash network ############  
    crash_num_nodes = 31
    #Start timer
    start_crash_time = time.time()

    #Send leave-calls to nodes
    crash_nodes(crash_num_nodes)

    #Check if ring is stable
    ring_stable = False
    counter = 0
    while ring_stable == False:
        counter += 1
        result = is_network_stable(list_nodes[-1], NUMBER_OF_NODES-crash_num_nodes)
        if result == True:
            print("RING IS STABLE")
            ring_stable = True
            break
        else:
            print("RING NOT STABLE", counter)
            if(counter == 50):
                sys.exit(1)
                break
        
        time.sleep(2)


    end_crash_time = time.time()
    crash_duration = end_crash_time - start_crash_time
    print(f"Time to become stable after {crash_num_nodes} crashes: {crash_duration:.2f} seconds")








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

