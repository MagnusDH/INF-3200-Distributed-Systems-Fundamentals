import requests
import sys
import json
import hashlib


def create_ID(server_name):
    #Create hash value for current server using SHA-1
    hash_object = hashlib.sha1(server_name.encode())  # encode string to bytes
    hash_hex = hash_object.hexdigest()      # hexadecimal string
    hash_int = int(hash_hex, 16)            # convert hex to integer

    #Convert hash value into a server_ID
    server_ID = hash_int % total_IDs
    
    #Check if ID has been created before
    while(server_ID in server_info):
        server_ID = (server_ID + 1) % total_IDs

    return int(server_ID)


def create_finger_table(node_ID):
    #Create a table with approximate IDs
    ish_finger_table = []
    for i in range(1, m+1):
        ish_ID=(node_ID + 2**(i-1)) % total_IDs
        
        ish_finger_table.append(ish_ID)
    
    #Sort ish finger_table
    ish_finger_table.sort()

    #Convert dictionary of actuall node IDs into a list
    list_actuall_IDs = []
    for key in server_info:
        list_actuall_IDs.append(key)
    #Sort the list
    list_actuall_IDs.sort()


    #Create actuall finger_table dict with ID as key and IP_address for server as value
    finger_table = {}
    for ish_ID in ish_finger_table:
        successor = None
        for ID in list_actuall_IDs:
            if(ID >= ish_ID):
                successor = ID
                break
        
        #Check if we looped around without finding a successor node
        if(successor == None):
            successor = list_actuall_IDs[0]
        
        #Add successor ID to finger table along with corresponding IPaddress
        finger_table[successor] = server_info[successor]["IP_address"]
    

    #Loop through finger table and remove the servers own ID if it is in the table 
    identical_key = None
    for key in finger_table:
        if(key == node_ID):
            identical_key = key
    if(identical_key != None):
        del finger_table[identical_key]


    #Find the ID of the predecessor server and store it
    predecessor = None
    for ID in list_actuall_IDs:
        if(ID < node_ID):
            predecessor = ID

    #If no predecessor was found, we looped around, therefore the biggest node ID is the predecessor
    if(predecessor == None):
        predecessor = list_actuall_IDs[-1]

    #Set predecessor    
    server_info[node_ID]["predecessor_ID"] = predecessor

    return finger_table 


def find_successor(node_ID, list_all_IDs):
    successor_ID = None
    list_all_IDs.sort()

    for ID in list_all_IDs:
        if(node_ID < ID):
            successor_ID = ID
            break

    if(successor_ID == None):
        successor_ID = list_all_IDs[0]


    return successor_ID


def find_predecessor(node_ID, list_all_IDs):
    predecessor_ID = None
    list_all_IDs.sort()

    for ID in list_all_IDs:
        if(ID < node_ID):
            predecessor_ID = ID
    
    if(predecessor_ID == None):
        predecessor_ID = list_all_IDs[-1]

    return predecessor_ID


if __name__ == "__main__":
    print("########## INITIALIZE_RING.PY ##########\n")

    
    #fetch the list of given server names 
    server_list = sys.argv[1:]

    global server_info
    server_info = {}

    #Total amount if IDs in the ring
    m = 10
    global total_IDs
    total_IDs = 2**m


    #How many entries a finger table should have
    global finger_table_entries
    finger_table_entries = 8

    list_all_IDs = []
    #Create list of IDs for each node
    for server in server_list:
        ID = create_ID(server)
        list_all_IDs.append(ID)
        server_info[ID] = {"IP_address":server, "finger_table": None, "successor_ID": None, "predecessor_ID": None}
    list_all_IDs.sort()
    print("Actuall nodes in system: ", list_all_IDs)
    
    
    #Create successor, predecessor and finger_table for each server
    for ID in server_info:
        server_info[ID]["successor_ID"] = find_successor(ID, list_all_IDs)
        server_info[ID]["predecessor_ID"] = find_predecessor(ID, list_all_IDs)
    
        finger_table = create_finger_table(ID)
        server_info[ID]["finger_table"] = finger_table



    #Send message to each server in the ring with their ID and finger table
    for ID in server_info:
        try:
            #Prepare a payload to send
            message_payload = {
                "ID": ID,
                "finger_table": server_info[ID]["finger_table"],
                "successor_ID": server_info[ID]["successor_ID"],
                "predecessor_ID": server_info[ID]["predecessor_ID"]
            }

            #Send message to server
            # print(f"initialize_ring.py: sending message to: {server_info[ID]["IP_address"]}")
            response = requests.post(f"http://{server_info[ID]["IP_address"]}/initialize", json=message_payload)
            # print(f"initialize_ring.py: recieved response: {response.text}")
        
        except requests.exceptions.Timeout:
            print("Server did not respond (timeout)")
        except requests.exceptions.ConnectionError:
            print("Could not connect to server")

