from flask import Flask, request, jsonify, Response
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
successors = [] #List of lists [ID, IP_address]
MAX_SUCCESSORS = 5
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
def is_ID_in_range(predecessor_ID, key_ID, node_ID):
    """
    Returns True if a given key_ID is in the range between a node and its predecessor
    Returns False otherwise
    """
    if(node_ID == predecessor_ID):
        return True
    
    #If my predecessorID is bigger than myself
    elif(predecessor_ID > node_ID):
        #ranges are from predecessor to maximum node IDs AND from 0 to node_ID
        if((key_ID >= 0 and key_ID <= node_ID) or (key_ID > predecessor_ID and key_ID <= ring_size)):
            return True
    
    #If my predecessorID is lower than my own ID
    elif(predecessor_ID < node_ID):
        #then ranges are from my own ID down to predecessorID+1
        if(key_ID <= node_ID and key_ID > predecessor_ID):
            return True
    
    #The key_ID is NOT in range
    return False


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
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


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


def update_finger_table():
    print("\nUPDATE_FINGER_TABLE()", flush=True)
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Create start-ID ranges for each entry in the finger_table
    for i in range(1, m+1):
        #Create an ID
        start_ID = (node_ID_IP[0] + (2**(i-1)) % (2**m))

        try:
            #Go thorugh the network and find which node_ID is responsible for this ID
            response = requests.post(f"http://{node_ID_IP[1]}/find_successor", json={"ID":start_ID})
            
            #Successor_node of ID is found
            if(response.status_code == 200):
                received_data = response.json()
                successor = received_data["successor"]
                if(successor[0] != node_ID_IP[0] and successor not in finger_table):
                    finger_table.insert(i, successor)
            
            else:
                print(f"    return status code was: {response.status_code}")
        
        #Node does not respond at all   
        except requests.exceptions.RequestException:
            print(f"    Finger_table[{i}] could not be updated -> Could not contact node: {node_ID_IP[0]}")
        

    #Keep length of m
    finger_table = finger_table[:m-1]


#DONE
def stabilize():
    """
    -This function is called every few seconds
    -Sends this nodes->ID/IP to successor
        -On the reciever side the receiver node can update its predecessor
    -recieves a successor and potentially updates the successor and the successors list
    
    -Updates the finger table
    
    -Sends a request to predecessor. If no response then predecessor is set to None 
    
    -Contacts the next successor and updates the successor list if the request failes
    """
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m

    
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
                        received_data = response.json()
                        given_predecessor_ID = int(received_data["predecessor"][0])
                        given_predecessor_IP = received_data["predecessor"][1]
                        given_successors_list = received_data["successors"]


                        #Given_predecessor is my new successor                
                        if(given_predecessor_ID != None and is_between(node_ID_IP[0], given_predecessor_ID, successors[0][0])):
                            new_successor = [given_predecessor_ID, given_predecessor_IP]
                            update_successors(new_successor, successors)
                        else:
                            #Update successors
                            update_successors(successors[0], given_successors_list)


                        #Check if predecessor is dead
                        if(predecessor != None):
                            if(is_node_alive(predecessor[1]) == False):
                                print(f"    My predecessor: {predecessor[0]} is dead")
                                predecessor = None

                        
                        #Update finger_table
                        update_finger_table()
                        
                        print(f"    Successors: {successors}")
                        print(f"    Predecessor: {predecessor}")
                        print(f"    finger_table: {finger_table}")
                        print(f"    Storage: {storage}")


                        #Break loop if stabilize() finishes
                        break
                    
                    #Node did not respond correctly
                    else:
                        print(f"    Could not contact successor {successors[0][0]}, popping from list")
                        #Remove successor from successors list
                        if(successors):
                            successors.pop(0)
                            print(f"    New successor: {successors[0][0]}")


                # #Node does not respond    
                # except requests.exceptions.RequestException:
                #     print(f"    Could not contact successor {successors[0][0]}, popping from list")
                #     #Remove successor from successors list
                #    if(successors):     
                #       successors.pop(0)
                #     print(f"    New successor: {successors[0][0]}")
            
                except Exception as error:
                    print(f"    Some error occured: '{error}'")
            
        
        #Stabilize again after n-seconds
        time.sleep(2)


def closest_preceding_node(ID):
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m

    
    if finger_table:
        for finger in reversed(finger_table):
            # Only consider fingers that are clockwise from self but before the target ID
            if(is_between(node_ID_IP[0], finger[0], ID)):
                return finger

    #Fallback to immediate successor if no suitable finger found
    if successors:
        return successors[0]

    #If neither finger table nor successor exists, we cannot forward
    return None


@app.route('/find_successor', methods=['POST'])
def find_successor():
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m
    # print("\nFIND_SUCCESSOR", flush=True)

    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500

    #Unpack ID from sender node
    received_data = request.get_json()
    ID = int(received_data["ID"])

    #I am the successor
    if(predecessor != None):
        if(is_between(predecessor[0], ID, node_ID_IP[0])):
            # print(f"    I am the successor of find_successor()")
            response_data = {"successor": node_ID_IP}
            #Return my ID/IP
            return response_data, 200


    #I have the successor
    if(successors):
        if(is_between(node_ID_IP[0], ID, successors[0][0])):
            # print(f"    I have the successor of find_successor()")
            response_data = {"successor": successors[0]}
            #Return my successors ID/IP
            return response_data, 200 


    #Forward request to closest node
    closest_node = closest_preceding_node(ID)
    if(closest_node == None or closest_node == node_ID_IP[0]):
        #Successor was not found and request can not be forwarded
        return "Successor not found", 404

    try:                                         
        print(f"    Forwarding find_successor-request to closest node:{closest_node[0]}...")
        response = requests.post(f"http://{closest_node[1]}/find_successor", json=received_data)

        #Return the exact response
        return Response(
            response=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/plain')
        ) 

    #Node does not respond at all
    except requests.exceptions.RequestException:
        print(f"    Could not contact node: {closest_node[1]}")
        return "Could not reach node", 503



    # #Forward request to my successor 
    # elif successors:
    #     print(f"    Forwarding GET-request to my successor:{successors[0][0]}...")
    #     response = requests.post(f"http://{successors[0][1]}/find_successor", json=received_data)

    #     #Return the exact response
    #     return Response(
    #         response=response.content,
    #         status=response.status_code,
    #         content_type=response.headers.get('Content-Type', 'text/plain')
    #     ) 


    #Successor was not found and request can not be forwarded
    return "Successor not found", 404


#DONE
@app.route('/ping', methods=['POST'])
def ping():   
    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        return "", 500

    else:
        return "Alive", 200
    

#DONE (update finger_table?)
@app.route('/help_stabilize', methods=['POST'])
def help_stabilize():
    """
    -Returns the current predecessor of this node
    -Potentially places contacting_node as the new predecessor 
    """
    print("\nHELP_STABILIZE()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Unpack ID/IP from sender node
    received_data = request.get_json()
    contacting_node_ID = int(received_data["node_ID_IP"][0])
    contacting_node_IP = received_data["node_ID_IP"][1]

    #The contacting_node is my new predecessor  
    if(predecessor==None or is_between(predecessor[0], contacting_node_ID, node_ID_IP[0])):
        predecessor = received_data["node_ID_IP"]
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


#DONE
@app.route('/storage/<key>', methods=['GET'])
def get_data(key):
    print("GET_DATA()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Client wants to retrieve
    key = key
                                                
    #Find the ID for this key
    key_ID = create_ID(key)

    #I am the only node in the ring
    if(predecessor==None and (not successors) and (not finger_table)):
        if(key in storage):
            print(f"    I have the requested data. Returning value to client")
            #return data
            return jsonify(storage[key]), 200

    #This server is responsible for the data
    if(is_ID_in_range(predecessor[0], key_ID, node_ID_IP[0])):
        print(f"     I am responsible for the requested data")
                                                    
        if(key in storage):
            print(f"    I have the requested data. Returning value to client")
            #return data
            return jsonify(storage[key]), 200
                                                        
        else:
            print(f"    The requested data does not exist...")
            #return "Key not found"   
            return "Key not found", 404         
                                                    

    #If the key_ID is in the range of my successor
    if(is_ID_in_range(node_ID_IP[0], key_ID, successors[0][0])):
        #Forward PUT-request to successor server
        print(f"    Forwarding get_data-request to node:{successors[0][0]}...")
        response = requests.get(f"http://{successors[0][1]}/storage/{key}")

        #Return the exact response
        return Response(
            response=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/plain')
        )


    #Forward PUT-request to closest node
    else:
        closest_node = closest_preceding_node(key_ID)
        if(closest_node == None or closest_node == node_ID_IP[0]):
            #Successor was not found and request can not be forwarded
            return "Successor not found", 404

        try:                                         
            print(f"    Forwarding find_successor-request to closest node:{closest_node[0]}...")
            response = requests.get(f"http://{closest_node[1]}/storage/{key}")

            #Return the exact response
            return Response(
                response=response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'text/plain')
            ) 

        #Node does not respond at all   
        except requests.exceptions.RequestException:
            print(f"    Could not contact node: {closest_node[1]}")
            return "Could not find key", 500


#DONE
@app.route('/storage/<key>', methods=['PUT'])
def put_data(key):
    print("\nPUT_DATA()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m



    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500

        
    #Client wants to store
    key = key
    value = request.get_data(as_text=True)

    #Create ID for key
    key_ID = create_ID(key)


    #I am the only node in the ring
    if(predecessor==None and (not successors) and (not finger_table)):
        print(f"    I am the only node in the ring. Storing key locally.")
        storage[key] = value
        return "OK", 200


    #This node is responsible for saving the data
    if(is_ID_in_range(predecessor[0], key_ID, node_ID_IP[0])):
        print(f"    I am responsible for saving the hashed key_ID: {key_ID}. Storing data...")
        #Store key and value
        storage[key] = value

        #send return message to client
        return "OK", 200
                        

    #The key_ID is in the range of my successor
    elif(is_ID_in_range(node_ID_IP[0], key_ID, successors[0][0])):                    
        #Forward PUT-request to successor server
        print(f"    Forwarding put_data-request to my successor: {successors[0][0]}...")
        response = requests.put(f"http://{successors[0][1]}/storage/{key}", data=value)

        #Return the exact response received from other node
        return Response(
            response=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'text/plain')
        )   


    #Forward PUT-request to closest server
    else:
        closest_node = closest_preceding_node(key_ID)
        if(closest_node == None or closest_node == node_ID_IP[0]):
            #Successor was not found and request can not be forwarded
            return "Successor not found", 404
        
        try:
            print(f"    Forwarding put_data-request to closest node: {closest_node[0]}...")
            response = requests.put(f"http://{closest_node[1]}/storage/{key}", data=value)

            
            #Return the exact response received from other node
            return Response(
                response=response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'text/plain')
            )  


        #Node does not respond at all   
        except requests.exceptions.RequestException:
            print(f"    Could not contact node: {closest_node[1]}")
            return "Could not store key", 500

        #Error storing key
        print(f"    OH SHIT, error")
        return "Could not store key", 500
    

#DONE
@app.route('/node-info', methods=['GET'])
def handle_node_info():
    print("\nHANDLE_NODE_INFO()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m

    # #Check if node is dead or inactive
    # if node_state in ["dead"]:
    #     print(f"    NODE: {node_ID_IP[0]} is dead!")
    #     return "", 500

    if(successors):
        successor = successors[0][1]
    else: 
        successor = node_ID_IP[1]
    
    info = {
        "node_hash": node_ID_IP[0],
        "successor": successor,
        "others": finger_table
    }
    return jsonify(info), 200, {"Content-type": "application/json"}


#DONE (update finger_table?)
@app.route('/leave', methods=['POST'])
def leave_ring():
    print("\nLEAVE_RING()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #return error if node is dead or not_member
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Set a flag to imply that you are no longer serving requests
    node_state = "not_member"

    #Send my successors list to my predecessor
    if(predecessor != None):
        message_payload = {
            "node_ID_IP": node_ID_IP,
            "successors": successors}
        requests.post(f"http://{predecessor[1]}/help_leave", json=message_payload)
    

    #Try to send message to a successor
    if(successors):
        for successor in successors:
            try:
                #Send my predecessor to my successor
                message_payload = {
                "node_ID_IP": node_ID_IP,
                "predecessor": predecessor}
                response = requests.post(f"http://{successor[1]}/help_leave", json=message_payload)

                if(response.status_code == 200):            
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
                if(successors):
                    successors.pop(0)
                    print(f"    New successor: {successors[0][0]}")
        

    #No nodes responded to the leave call
    print(f"    No nodes repsonded to leave-call, but I'm leaving anyways")
    return "OK", 200


#DONE (update finger_table?)
@app.route('/help_leave', methods=['POST'])
def help_leave():
    """
    -Receives a leaving-call from a leaving node
    -Assigns the given predecessor and successors list as new nodes, if they are in the right place
    """
    print("\nHELP_LEAVE()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500

    #Receive message
    received_data = request.get_json()
    contacting_node_ID = int(received_data["node_ID_IP"][0])
    contacting_node_IP = received_data["node_ID_IP"][1]
    
    #My successor is leaving the circle or the contacting node is my actuall successor
    if((successors!=None and contacting_node_ID==successors[0][0])
    or 
    is_between(node_ID_IP[0], contacting_node_ID, successors[0][0])
    ):
        #Take over his successors list
        successors = received_data["successors"]
        return "OK", 200

    
    #My predecessor is leaving or the contacting node is my actuall predecessor
    elif((predecessor!=None and contacting_node_ID == predecessor[0])
    or 
    is_between(predecessor[0], contacting_node_ID, node_ID_IP[0])
    ):
        #Take over his predecessor
        predecessor = received_data["predecessor"]
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


#DONE (update finger_table?)
@app.route('/sim-recover', methods=['POST'])
def sim_recover():
    print("\nSIM_RECOVER()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m

    node_state = "new"

    #I am the only node in the ring
    if(predecessor==None and (not successors) and (not finger_table)):
        #return data
        return "OK", 200

    else:
        #Try to contact any known node to re-enter the ring
        known_nodes = []
        if(predecessor != None):
            known_nodes.append(predecessor)
        if(successors):
            known_nodes.extend(successors)
        if(finger_table):
            known_nodes.extend(finger_table)

        #If there are any nodes to contact, try to join ring
        if(known_nodes):
            print("KNOWN NODES: ", known_nodes)
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
            # return "Could not rejoin ring, no nodes responded", 404
    
    return "OK", 200


#DONE
@app.route('/join', methods=['POST'])
def join_ring():
    """
    -initiates this node to join an existing network via given node
    -
    """
    print("\nJOIN_RING()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Try to contact existing node
    try:
        #Get the IP-address of existing node
        existing_node = request.args.get('nprime')

        #Contact existing_node and provide my ID
        # print(f"    Contacting {existing_node} to join network...")
        request_payload = {"joining_node": node_ID_IP}
        response = requests.post(f"http://{existing_node}/help_join", json=request_payload)

        #Unpack response
        if(response.status_code == 200):
            received_data = response.json()
            new_successor = received_data["successor"]
            new_successor_list = received_data["successors"]
            new_predecessor = received_data["predecessor"]

            #Update successor list, predecessor and finger_table
            update_successors(new_successor, new_successor_list)
            predecessor = new_predecessor
            # finger_table.insert(0, new_successor)
            update_finger_table()
            

            #Update node state
            node_state = "active"

            return "OK", 200#, {"Content-type": "text/plain"}
        
        #Node did not respond correctly
        else:
            return "Error: could not join ring", 500
    

    #Node does not respond at all   
    except requests.exceptions.RequestException:
        print(f"    Could not contact existing node: {existing_node}")


#DONE (update finger_table?)
@app.route('/help_join', methods=['POST'])
def help_join():
    print("\nHELP_JOIN()")
    global storage, node_ID_IP, successors, predecessor, finger_table, node_state, m


    #Check if node is dead or inactive
    if node_state in ["dead", "not_member"]:
        print(f"    NODE: {node_ID_IP[0]} is dead or not_member!")
        return "", 500


    #Recieve data from joining node
    received_data = request.get_json()
    joining_node = received_data["joining_node"]
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
        successors.insert(0, (joining_ID, joining_IP))
        predecessor = [joining_ID, joining_IP]
        # finger_table.insert(0, [joining_ID, joining_IP])

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
        predecessor = [joining_ID, joining_IP]

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
        new_successor = [joining_ID, joining_IP]
        update_successors(new_successor, successors)


        #send payload
        return jsonify(response_payload), 200
    
    
    #I don't know the successor
    else:
        closest_node = closest_preceding_node(joining_ID)
        if(closest_node == None or closest_node == node_ID_IP[0]):
            #Successor was not found and request can not be forwarded
            return "Successor not found", 404
        
        #Try to forward help-join request
        try:
            print(f"    Forwarding help_join-request to {closest_node[0]} to find successor")
            response = requests.post(f"http://{closest_node[1]}/help_join", json=received_data)

            
            #Return the exact response received from other node
            return Response(
                response=response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'text/plain')
            )  

        
        #Node does not respond    
        except requests.exceptions.RequestException:
            print(f"    Node: {closest_node[0]} did not respond to forwarding help_join-request")
        
        #No successor or predecessor node was found
        return "Not found", 404
        

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Missing argument: <host:port>")
        sys.exit(1)
    
    host, port = sys.argv[1].split(':')
    ID = create_ID(f"{host}:{port}")
    node_ID_IP = [ID, f"{host}:{port}"]
    node_status = "new"
    
    print(f"Node ID: {node_ID_IP[0]}")
    print(f"Node_IP: {node_ID_IP[1]}")
    print(f"Node status: {node_status}")


    #Start stabilize thread
    stabilize_thread = threading.Thread(target=stabilize, daemon=True)
    stabilize_thread.start()

    app.run(host=host, port=int(port), use_reloader=False)
