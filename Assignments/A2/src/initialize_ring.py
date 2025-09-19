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

    return server_ID


def create_finger_table(node_ID):
    #Create a table with "m" entries
    finger_table = []
    for i in range(1, finger_table_entries+1):
        ish_ID=(node_ID + 2**(i-1)) % total_IDs
        
        finger_table.append(ish_ID)
        

    #Correct the IDs in the finger table to correspond to the actual server IDs
    for i in range(len(finger_table)):
        pos_counter=0   #Counter to check if we have looped around the IDs
        for ID in server_info:
            #Return current ID if it is the same or the next server ID 
            if(ID >= finger_table[i]):
                finger_table[i] = ID
                break

            else:
                pos_counter+=1
            
            #Check if we have looped around
            if(pos_counter >= len(server_info)):
                #find the lowest key in the server_info dict
                lowest_key = min(server_info)

                #Place the first server ID because we looped around
                finger_table[i] = lowest_key  
        

    #Create new finger table dict to contain IPaddresses
    new_finger_table = {}
    #Go trhough each entry in the finger_table list
    for ID in finger_table:
        if(ID in server_info):
            new_finger_table[ID] = server_info[ID]["IP_address"]
        else:
            print("ERROR: somethings wrong when making finger table")

    return new_finger_table



if __name__ == "__main__":
    print("########## INITIALIZE_RING.PY ##########\n")
    
    #fetch the list of given server names 
    server_list = sys.argv[1:]

    global server_info
    server_info = {}

    #Total amount if IDs in the ring
    global total_IDs
    total_IDs = 2**8

    #How many entries a finger table should have
    global finger_table_entries
    finger_table_entries = 8


    #Create list of IDs for each node
    for server in server_list:
        ID = create_ID(server)

        server_info[ID] = {"IP_address":server, "finger_table": None}
    
    #Create finger tables for each server
    for ID in server_info:
        finger_table = create_finger_table(ID)
        server_info[ID]["finger_table"] = finger_table


    #Send message to each server in the ring with their ID and finger table
    for ID in server_info:
        try:
            #Prepare a payload to send
            message_payload = {
                "ID": ID,
                "finger_table": server_info[ID]["finger_table"]
            }

            #Send message to server
            # print(f"initialize_ring.py: sending message to: {server_info[ID]["IP_address"]}")
            response = requests.post(f"http://{server_info[ID]["IP_address"]}/initialize", json=message_payload)
            # print(f"initialize_ring.py: recieved response: {response.text}")
        
        except requests.exceptions.Timeout:
            print("Server did not respond (timeout)")
        except requests.exceptions.ConnectionError:
            print("Could not connect to server")

