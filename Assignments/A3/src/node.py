from flask import Flask, request, jsonify
import requests
import sys
import os
import hashlib
import threading
import time

app = Flask(__name__)

# Silence werkzeug logs
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

#Internal info
storage = {}
node_ID_IP = None
successors = [] #List of tuples (ID, IP_address)
MAX_SUCCESSORS = 2
predecessor = None
finger_table = []

#states:
    #new (newly started node)
    #member (is alive and part of the ring)
    #not_member (is alive but not part of the ring anymore and does not want to be part of ring)
    #dead (node does not respond to anyting)
node_state = "new"

#Total number of IDs in chord ring
m = 10
ring_size = 2**m


#DONE
def create_ID(IP_address):
    """
    Hashes the given IP_address and returns a unique integer ID and hash string for this node
    """
    #Create hash value for current server using SHA-1
    hash_object = hashlib.sha1(IP_address.encode())  # encode string to bytes
    hash_hex = hash_object.hexdigest()      # hexadecimal string
    hash_int = int(hash_hex, 16)            # convert hex to integer

    #Convert hash value into a server_ID
    ID = hash_int % ring_size
    
    return int(ID)


#DONE
def is_between(node_A_ID, current_node_ID, node_B_ID):
    """
    Returns True if current_node is clockwise between node_A and node_B
    in a circular ID space.

    node_A = the ID of the first node
    current_node = the ID of the node to be placed in between
    node_B_hash = the ID of the last node
    """
    #Normal case, circle is not wraping around
    if node_A_ID < node_B_ID:
        return node_A_ID < current_node_ID <= node_B_ID

    #Case where circle wraps around
    elif node_A_ID > node_B_ID:
        # Example: A=30, B=10, new=40 -> True, new=5 -> True
        return current_node_ID > node_A_ID or current_node_ID <= node_B_ID

    else:
        # node_A_hash == node_B_hash, single-node ring
        return True


#DONE
def is_node_alive(node_IP):
    """Returns True if node responds to a simple get-request"""
    try:
        #send ping
        response = requests.post(f"http://{node_IP}/ping", timeout=2)
        
        #node responded successfully
        if(response.status_code == 200):
            return True
        else:
            return False

    #Catch any requests-related errors
    except requests.exceptions.RequestException:
        return False


#DONE
def update_successors(new_successor, new_successor_list):
    """
    -Checks every node in the new successors list to see if they are alive
    -Makes sure this nodes ID is not in the list
    -If no node is alive, then the old successors list is kept 
    """
    print("\nUPDATE_SUCCESSORS()")
    global successors

    tmp_successors = [new_successor] + new_successor_list[:MAX_SUCCESSORS-1]
    new_successors = []

    #Verify that each successor is alive
    for successor in tmp_successors:
        #Do not add node if it is my own ID
        if(successor[0] != node_ID_IP[0]):
            if(is_node_alive(successor[1]) == True):
                #Node is alive
                new_successors.append(successor)
    
    #If new_successors contains at least 1 node
    if new_successors:
        successors = new_successors


#DONE (fix finger_table)
def stabilize():
    """
    -This function is called every few seconds
    -Sends this nodes->ID/IP to successor
        -On the reciever side the receiver node can update its predecessor
    -recieves a successor and potentially updates the successor and the successors list
    
    -FIX FINGER TABLE!!!!!!!!!!
    
    -Sends a request to predecessor. If no response then predecessor is set to None 
    
    -Contacts the next successor and updates the successor list if the request failes
    """
    global successors, predecessor
    
    while(True):
        print("\nSTABILIZE()", flush=True)
        
        #Check if node is dead or inactive
        if node_state in ["dead", "not_member"]:
            print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
            time.sleep(2)
            continue
        

        #Node is not alone in the ring
        if(successors):
            for successor in successors:
                #Try to stabilize node
                try:
                    #Send my ID/IP to my successor, giving him the chance to change me as his predecessor
                    request_payload = {"node_ID_IP": node_ID_IP}
                    response = requests.post(f"http://{successors[0][1]}/help_stabilize", json=request_payload)
                    
                    #Node responded correctly
                    if(response.status_code == 200):
                        #Unpack my successors responce with predecessor
                        recieved_data = response.json()
                        given_predecessor_ID = int(recieved_data["predecessor"][0])
                        given_predecessor_IP = recieved_data["predecessor"][1]
                        given_successors_list = recieved_data["successors"]



                        #Given_predecessor is my new successor                
                        if(given_predecessor_ID != None and is_between(node_ID_IP[0], given_predecessor_ID, successors[0][0])):
                            new_successor = (given_predecessor_ID, given_predecessor_IP)
                            update_successors(new_successor, successors)
                        else:
                            #Update successors
                            update_successors(successors[0], given_successors_list)


                        #Check if predecessor is dead
                        if(predecessor != None):
                            if(is_node_alive(predecessor[1]) == False):
                                print(f"    My predecessor: {predecessor[0]} is dead")
                                predecessor = None

                        
                        #Call "fix_fingers()" to make sure the entries in its finger table are correct:
                            #HOW?
                        
                        print(f"    Successors: {successors}")
                        print(f"    Predecessor: {predecessor}")
                        print(f"    finger_table: {finger_table}")

                        #Break loop if stabilize() finishes
                        break
                    
                    #Node did not respond correctly
                    else:
                        print(f"    Could not contact successor {successors[0][0]}, popping from list")
                        #Remove successor from successors list
                        successors.pop(0)
                        print(f"    New successor: {successors[0][0]}")


                # #Node does not respond    
                # except requests.exceptions.RequestException:
                #     print(f"    Could not contact successor {successors[0][0]}, popping from list")
                #     #Remove successor from successors list
                #     successors.pop(0)
                #     print(f"    New successor: {successors[0][0]}")
            
                except Exception as error:
                    print(f"    Some error occured: '{error}'")
            
        
        #Stabilize again after n-seconds
        time.sleep(2)


#DONE
@app.route('/ping', methods=['POST'])
def ping():   
    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        return "", 500

    else:
        return "Alive", 200
    

#DONE
@app.route('/help_stabilize', methods=['POST'])
def help_stabilize():
    """
    -Returns the current predecessor of this node
    -Potentially places contacting_node as the new predecessor 
    """
    print("\nHELP_STABILIZE()")

    global predecessor

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Unpack ID/IP from sender node
    recieved_data = request.get_json()
    contacting_node_ID = int(recieved_data["node_ID_IP"][0])
    contacting_node_IP = recieved_data["node_ID_IP"][1]

    #The contacting_node is my new predecessor  
    if(predecessor==None or is_between(predecessor[0], contacting_node_ID, node_ID_IP[0])):
        predecessor = recieved_data["node_ID_IP"]
        response_data = {
            "predecessor": predecessor,
            "successors": successors
        }
    
    #I keep my old predecessor
    else:
        response_data = {
            "predecessor": predecessor,
            "successors": successors
        }

    #Send my predecessor to node
    return response_data, 200 



@app.route('/storage/<key>', methods=['GET'])
def get_key(key):
    print("GET_KEY()")

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    val = storage.get(key, None)
    if val is None:
        return "Not Found", 404, {"Content-type": "text/plain"}
    else:
        return val, 200, {"Content-type": "text/plain"}
    


@app.route('/storage/<key>', methods=['PUT'])
def handle_storage_put(key):

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500

    data = request.get_data(as_text=True)
    storage[key] = data
    return "OK", 200, {"Content-type": "text/plain"}


#DONE
@app.route('/node-info', methods=['GET'])
def handle_node_info():
    print("\nHANDLE_NODE_INFO()")
    #Check if node is dead or inactive
    if node_state in ["dead"]:
        print(f"    NODE: {node_ID_IP[0]} is dead!")
        return "", 500


    info = {
        "node_hash": node_ID_IP[0],
        "successor": successors[0][1],
        "others": finger_table
    }
    return jsonify(info), 200, {"Content-type": "application/json"}


#Works, but needs to fix finger_table
@app.route('/leave', methods=['POST'])
def leave_ring():
    print("\nLEAVE_RING()")
    global successors, predecessor, finger_table, node_state, node_ID_IP

    #return error if node is dead or not_member
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Set a flag to imply that you are no longer serving requests
    node_state = "not_member"

    #Send my successors list to my predecessor
    message_payload = {
        "node_ID_IP": node_ID_IP,
        "successors": successors}
    requests.post(f"http://{predecessor[1]}/help_leave", json=message_payload)
    

    #Try to send message to a successor
    for successor in successors:
        try:
            #Send my predecessor to my successor
            message_payload = {
            "node_ID_IP": node_ID_IP,
            "predecessor": predecessor}
            response = requests.post(f"http://{successor[1]}/help_leave", json=message_payload)

            if(response.status_code == 200):
                #Update finger tables?
                    #Nodes that have your node in their finger tables should replace it with your successor (or predecessor) if known.
                    #For this assignment, finger table updates are optional, but it improves stability.
                
                #Some implementations notify other nodes (successors, predecessors, finger tables) to maintain robustness.
                #In your assignment, notifying just the immediate neighbors is enough.
            
                #Reset my own state, but keep successors, predecessor and finger_table
                node_state = "not_member"

                print(f"    Node: {node_ID_IP[0]} left the circle")
                return "OK", 200#, {"Content-type": "text/plain"}
            else:
                print(f"    Response status code was not 200")

        #Node does not respond    
        except requests.exceptions.RequestException:
            print(f"    Could not contact successor {successors[0][0]}, popping from list")
            #Remove successor from successors list
            successors.pop(0)
            print(f"    New successor: {successors[0][0]}")
    

    #No nodes responded to the leave call
    print(f"    No nodes repsonded to leave-call, but I'm leaving anyways")
    return "OK", 200


#DONE
@app.route('/help_leave', methods=['POST'])
def help_leave():
    """
    -Receives a leaving-call from a leaving node
    -Assigns the given predecessor and successors list as new nodes, if they are in the right place
    """
    global successors, predecessor, node_ID_IP, node_state
    print("\nHELP_LEAVE()")

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500

    #Receive message
    recieved_data = request.get_json()
    contacting_node_ID = int(recieved_data["node_ID_IP"][0])
    contacting_node_IP = recieved_data["node_ID_IP"][1]
    
    #My successor is leaving the circle or the contacting node is my actuall successor
    if((successors!=None and contacting_node_ID==successors[0][0])
    or 
    is_between(node_ID_IP[0], contacting_node_ID, successors[0][0])
    ):
        #Take over his successors list
        successors = recieved_data["successors"]
        return "OK", 200

    
    #My predecessor is leaving or the contacting node is my actuall predecessor
    elif((predecessor!=None and contacting_node_ID == predecessor[0])
    or 
    is_between(predecessor[0], contacting_node_ID, node_ID_IP[0])
    ):
        #Take over his predecessor
        predecessor = recieved_data["predecessor"]
        return "OK", 200

    #Return 
    else:
        return "I'm a teapot", 418


#Done
@app.route('/sim-crash', methods=['POST'])
def simulate_crash():
    global node_state
    node_state = "dead"
        
    return "OK", 200#, {"Content-type": "text/plain"}


#DONE (Fix finger_table????)
@app.route('/sim-recover', methods=['POST'])
def sim_recover():
    print("\nSIM_RECOVER()")
    global predecessor, successors, finger_table, node_state

    node_state = "new"

    #Try to contact any known node to re-enter the ring
    known_nodes = [predecessor] + successors + finger_table 

    for node in known_nodes:
        try:
            response = requests.post(f"http://{node_ID_IP[1]}/join?nprime={node[1]}")

            if(response.status_code == 200):
                return "OK", 200, {"Content-type": "text/plain"}
            #Node responded incorrectly    
            else:
                print(f"    Could not contact node {node[0]} to rejoin circle. trying a new one")
        
        #Node does not respond    
        except requests.exceptions.RequestException:
            print(f"    Could not contact node: {node[0]}, trying a new one")

    #Could not rejoin ring
    return "Could not rejoin ring, no nodes responded", 404


#DONE
@app.route('/join', methods=['POST'])
def join_ring():
    """
    -initiates this node to join an existing network
    -A request is sent to this node with an existing ring node as argument
    -
    """
    print("\nJOIN_RING()")
    global predecessor, node_state

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Try to contact existing node
    try:
        #Get the IP-address of existing node
        existing_node = request.args.get('nprime')

        #Contact existing_node and provide my ID
        print(f"    Contacting {existing_node} to join network...")
        request_payload = {"joining_node": node_ID_IP}
        response = requests.post(f"http://{existing_node}/help_join", json=request_payload)

        #Unpack response
        if(response.status_code == 200):
            recieved_data = response.json()
            new_successor = recieved_data["successor"]
            new_successor_list = recieved_data["successors"]
            new_predecessor = recieved_data["predecessor"]

            #Update successor list and predecessor
            update_successors(new_successor, new_successor_list)
            predecessor = new_predecessor

            #Update node state
            node_state = "active"

            return "OK", 200#, {"Content-type": "text/plain"}
        
        #Node did not respond correctly
        else:
            return "Error: could not join ring", 500
    

    #Node does not respond at all   
    except requests.exceptions.RequestException:
        print(f"    Could not contact existing node: {existing_node}")


#DONE (only fix finger_table forwarding)
@app.route('/help_join', methods=['POST'])
def help_join():
    print("\nHELP_JOIN()")
    global predecessor

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Recieve data from joining node
    recieved_data = request.get_json()
    joining_node = recieved_data["joining_node"]
    joining_ID = int(joining_node[0])
    joining_IP = joining_node[1]

    #Find out who the successor of joining_node is        
    #Only one node in the circle
    if not successors and predecessor == None:
        print("     Only one node in ring")
        response_payload = {
            "successor": node_ID_IP,
            "successors": successors,
            "predecessor": node_ID_IP
        }

        #Update this nodes predecessor to the joining_node
        successors.append((joining_ID, joining_IP))
        predecessor = (joining_ID, joining_IP)

        #send payload
        return jsonify(response_payload), 200


    #I am the successor
    elif(is_between(predecessor[0], joining_ID, node_ID_IP[0])):
        response_payload = {
            "successor": node_ID_IP,
            "successors": successors,
            "predecessor": predecessor
        }

        #Update this nodes predecessor to the joining_node
        predecessor = (joining_ID, joining_IP)

        #send payload
        return jsonify(response_payload), 200
    

    #I am the predecessor
    elif(is_between(node_ID_IP[0], joining_ID, successors[0][0])):
        response_payload = {
            "successor": successors[0],
            "successors": successors,
            "predecessor": node_ID_IP
        }

        #Update my successor
        new_successor = (joining_ID, joining_IP)
        update_successors(new_successor, successors)

        #send payload
        return jsonify(response_payload), 200
    
    
    #I don't know the successor
    # elif(joining_ID > node_ID_IP[0] and joining_ID > successors[0][0]):
    else:
        #Forward the request to closest node for joining_ID
        if(finger_table):
            closest_node = None
            for ID in finger_table:
                if(joining_ID > ID[0]):
                    closest_node = ID

            #Close node was not found, send to the largest node in finger_table
            if(closest_node == None):
                # list_finger_table_IDs = list(finger_table.keys())
                # list_finger_table_IDs.sort()
                closest_node = finger_table[-1]
        else:
            closest_node = successors[0]
        
        print(f"    Forwarding request to {closest_node[0]} to find successor")
        #Try to forward request
        try:
            response = requests.post(f"http://{closest_node[1]}/help_join", json=recieved_data)

            #send payload
            return response.text, response.status_code
        
        #Node does not respond    
        except requests.exceptions.RequestException:
            print(f"    Node: {closest_node[0]} did not respond to forwarding request")
        

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Missing argument: <host:port>")
        sys.exit(1)
    
    host, port = sys.argv[1].split(':')
    ID = create_ID(f"{host}:{port}")
    node_ID_IP = (ID, f"{host}:{port}")
    node_status = "new"
    
    print(f"Node ID: {node_ID_IP[0]}")
    print(f"Node_IP: {node_ID_IP[1]}")
    print(f"Node status: {node_status}")


    #Start stabilize thread
    stabilize_thread = threading.Thread(target=stabilize, daemon=True)
    stabilize_thread.start()

    app.run(host=host, port=int(port), use_reloader=False)
