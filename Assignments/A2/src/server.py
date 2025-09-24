# from flask import Flask, request, jsonify
# import socket
# import sys
# import hashlib
# import requests


# # Silence werkzeug logs
# import logging
# logging.getLogger('werkzeug').setLevel(logging.ERROR)

# #Set up Flask application
# app = Flask(__name__)

# #Get the name of the current node
# HOSTNAME = socket.gethostname().split('.')[0]

# #Port number given by user
# if len(sys.argv) > 1:
#     PORT = int(sys.argv[1])
# else:
#     PORT = 5000 #A default port


# #the data that is stored in this server
# stored_data = {}

# m=10
# global total_IDs
# total_IDs = 2**m

# my_ID = None
# finger_table = {}
# predecessor_ID = None
# successor_ID = None


# #This code wil be run when someone visits the given url-path
# @app.route("/")
# def home():
#     print("HOME()")
#     return f"This is server: {ID} running at: {HOSTNAME}:{PORT}"

# @app.route("/initialize", methods=["POST"])
# def initialize_server():
#     print("INITIALIZE_SERVER()")

#     #Recieve data
#     recieved_data = request.get_json()

#     #Unpack data
#     recieved_ID = recieved_data.get("ID")
#     recieved_finger_table = recieved_data.get("finger_table")
#     recieved_successor_ID = recieved_data.get("successor_ID")
#     recieved_predecessor_ID = recieved_data.get("predecessor_ID")

#     #Assign values to global varibales
#     global my_ID
#     global finger_table
#     global predecessor_ID
#     global successor_ID

#     my_ID = int(recieved_ID)
#     for key in recieved_finger_table:
#         finger_table[int(key)] = recieved_finger_table[key]
#     successor_ID = int(recieved_successor_ID)
#     predecessor_ID = int(recieved_predecessor_ID)
    
#     print(f"    My server ID: {my_ID}")
#     print(f"    My finger_table: {finger_table}")
#     print(f"    My successor_ID: {successor_ID}")
#     print(f"    My predecessor_ID: {predecessor_ID}")

#     return f"{HOSTNAME}:{PORT} is initialized.", 200


# @app.route("/network", methods=["GET"])
# def get_list_nodes():
#     #return list of known nodes as json and status code 200
#     known_nodes = []
#     for ID in finger_table:
#         known_nodes.append(finger_table[ID])

#     return jsonify(known_nodes), 200


# @app.route("/put", methods=["POST"])
# def put_data():

#     print("PUT_DATA()")

#     #Recieve data
#     recieved_data = request.get_json()
    
#     #Unpack data
#     key = recieved_data["data"][0]
#     value = recieved_data["data"][1]

#     # print(f"    Recieved data: {recieved_data}")
    
#     #Create integer hash value for the key using SHA-1
#     key_ID = hashlib.sha1(key.encode('utf-8')).hexdigest()
#     key_ID = int(key_ID, 16)
#     key_ID = key_ID % total_IDs


#     #MAKE CHECKS TO SEE WHERE THE DATA SHOULD BE STORED

#     #This server is responsible for saving the data
#     if(is_ID_in_range(predecessor_ID, my_ID, key_ID) == True):
#         # print(f"     I am server: {my_ID} and I'm responsible for saving the data. Saving data...")
#         #Store key and value
#         global stored_data
#         stored_data[key] = value

#         print(f"    I stored the data: {key}:{stored_data[key]}")

#         #send return message to client
#         return f"Node:{my_ID} has stored the data", 200


#     #If the key_ID is in the range of my successor
#     if(is_ID_in_range(my_ID, successor_ID, key_ID) == True):
#         # print(f"    I can not store the data, but the key_ID:{key_ID} is in range for my successor")
        
#         #Forward PUT-request to successor server
#         # print(f"    Forwarding PUT-request to server:{successor_ID}...")
#         response = requests.post(f"http://{finger_table[successor_ID]}/put", json=recieved_data)
#         # print(f"    Received response from server:{finger_table[successor_ID]}: {response.text}")

#         return response.text, 200


#     #If the key is not in range, forward PUT-request to the largest ID in the finger table but still less than the key_ID
#     else:
#         # print("    The key_ID is not in range of my successor, so I'm finding the closest server")
#         closest_server = None

#         for ID in finger_table:
#             if(ID < key_ID):
#                 closest_server = ID
        
#         if(closest_server == None):
#             list_finger_table_IDs = list(finger_table.keys()).sort()
#             closest_server = list_finger_table_IDs[-1] 
        
#         # print(f"    Forwarding the PUT-request to server: {closest_server}...")
#         response = requests.post(f"http://{finger_table[closest_server]}/put", json=recieved_data)
#         # print(f"    Received response from server:{finger_table[closest_server]}: {response.text}")

#         return response.text, 200



# @app.route("/get", methods=["GET"])
# def get_data():
#     print("GET_DATA()")

#     #Recieve data
#     key = request.args.get("key")

#     # print(f"    Key the client want me to retrieve: {key}")

#     #Hash the recieved key to find which node it belongs to using SHA-1
#     key_ID = hashlib.sha1(key.encode('utf-8')).hexdigest()
#     key_ID = int(key_ID, 16)
#     key_ID = key_ID % total_IDs

#     # print(f"    The key_ID is: {key_ID}")


#     #MAKE CHECKS TO SEE WHERE THE DATA SHOULD BE STORED

#     #This server is responsible for saving the data
#     if(is_ID_in_range(predecessor_ID, my_ID, key_ID) == True):
#         # print(f"     I am server: {my_ID} and I should have the requested data. checking...")
        
#         #Check if key is contained in internal hashtable/dictionary
#         if(key in stored_data):
#             print(f"    I have the requested data. Returning value to client")
#             return stored_data[key], 200 
            
#         else:
#             print(f"    The requested data does not exist...")
#             return f"Requested data was not found", 404            
        
#     #If the key_ID is in the range of my successor
#     if(is_ID_in_range(my_ID, successor_ID, key_ID) == True):
#         # print(f"    I do not have the data, but the key_ID:{key_ID} is in range for my successor")
        
#         #Forward PUT-request to successor server
#         # print(f"    Forwarding GET-request to server:{successor_ID}...")
#         response = requests.get(f"http://{finger_table[successor_ID]}/get?key={key}")
#         # print(f"    Received response from server:{finger_table[successor_ID]}: {response.text}")

#         return response.text, 200

#     #If the key is not in range, forward PUT-request to the largest ID in the finger table but still less than the key_ID
#     else:
#         # print("    The key_ID is not in range of my successor, so I'm finding the closest server")
#         closest_server = None

#         for ID in finger_table:
#             if(ID < key_ID):
#                 closest_server = ID
        
#         if(closest_server == None):
#             list_finger_table_IDs = list(finger_table.keys()).sort()
#             closest_server = list_finger_table_IDs[-1] 
        
#         # print(f"    Forwarding the GET-request to closest server: {closest_server}")
#         response = requests.get(f"http://{finger_table[closest_server]}/get?key={key}")
#         # print(f"    Received response from server:{finger_table[closest_server]}: {response.text}")

#         return response.text, 200


# """
# Returns True if a given key_ID is in the range between a node and its predecessor
# Returns False otherwise
# """
# def is_ID_in_range(predecessor_ID, node_ID, key_ID):
#     if(node_ID == predecessor_ID):
#         return True
    
#     #If my predecessorID is bigger than myself
#     elif(predecessor_ID > node_ID):
#         #ranges are from predecessor to maximum node IDs AND from 0 to node_ID
#         if((key_ID >= 0 and key_ID <= node_ID) or (key_ID > predecessor_ID and key_ID <= total_IDs)):
#             return True
    
#     #If my predecessorID is lower than my own ID
#     elif(predecessor_ID < node_ID):
#         #then ranges are from my own ID down to predecessorID+1
#         if(key_ID <= node_ID and key_ID > predecessor_ID):
#             return True
    
#     #The key_ID is NOT in range
#     return False



# if __name__ == "__main__":
#     print(f"\n########## Code running at server: {HOSTNAME}:{PORT} ##########")
    
#     app.run(host="0.0.0.0", port=PORT, use_reloader=False)  #"0.0.0.0" allows all machines to connect to the node














from flask import Flask, request, jsonify, Response
import socket
import sys
import hashlib
import requests


# Silence werkzeug logs
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

#Set up Flask application
app = Flask(__name__)

#Get the name of the current node
HOSTNAME = socket.gethostname().split('.')[0]

#Port number given by user
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 5000 #A default port


#the data that is stored in this server
stored_data = {}

m=10
global total_IDs
total_IDs = 2**m

my_ID = None
finger_table = {}
predecessor_ID = None
successor_ID = None


#This code wil be run when someone visits the given url-path
@app.route("/")
def home():
    print("HOME()")
    return f"This is server: {ID} running at: {HOSTNAME}:{PORT}"

@app.route("/initialize", methods=["POST"])
def initialize_server():
    print("INITIALIZE_SERVER()")

    #Recieve data
    recieved_data = request.get_json()

    #Unpack data
    recieved_ID = recieved_data.get("ID")
    recieved_finger_table = recieved_data.get("finger_table")
    recieved_successor_ID = recieved_data.get("successor_ID")
    recieved_predecessor_ID = recieved_data.get("predecessor_ID")

    #Assign values to global varibales
    global my_ID
    global finger_table
    global predecessor_ID
    global successor_ID

    my_ID = int(recieved_ID)
    for key in recieved_finger_table:
        finger_table[int(key)] = recieved_finger_table[key]
    successor_ID = int(recieved_successor_ID)
    predecessor_ID = int(recieved_predecessor_ID)
    
    print(f"    My server ID: {my_ID}")
    print(f"    My finger_table: {finger_table}")
    print(f"    My successor_ID: {successor_ID}")
    print(f"    My predecessor_ID: {predecessor_ID}")

    return f"{HOSTNAME}:{PORT} is initialized.", 200

#DONE
@app.route("/network", methods=["GET"])
def get_list_nodes():
    #return list of known nodes as json and status code 200
    known_nodes = []
    for ID in finger_table:
        known_nodes.append(finger_table[ID])

    return jsonify(known_nodes), 200


@app.route("/storage/<key>", methods=["PUT"])
def put_data(key):
    # print("PUT_DATA()")
    
    #Client wants to store
    key = key
    value = request.data.decode("utf-8")

    #Create integer hash value for the key using SHA-1
    key_ID = hashlib.sha1(key.encode('utf-8')).hexdigest()
    key_ID = int(key_ID, 16)
    key_ID = key_ID % total_IDs


    #This server is responsible for saving the data
    if(is_ID_in_range(predecessor_ID, my_ID, key_ID) == True):
        # print(f"     I am responsible for saving the hashed key_ID: {key_ID}. Storing data...")
        #Store key and value
        global stored_data
        stored_data[key] = value

        #send return message to client
        # return f"OK", 200
        return Response("OK", status=200, mimetype='text/plain')
    

    #If the key_ID is in the range of my successor
    if(is_ID_in_range(my_ID, successor_ID, key_ID) == True):
        
        #Forward PUT-request to successor server
        # print(f"    Forwarding PUT-request to my successor: {successor_ID}...")
        response = requests.put(f"http://{finger_table[successor_ID]}/storage/"+key, value)

        # return response.text, response.status_code
        return Response(response.text, status=response.status_code, mimetype='text/plain')         


    #Forward PUT-request to closest server
    else:
        closest_server = None

        for ID in finger_table:
            if(ID < key_ID):
                closest_server = ID
        
        if(closest_server == None):
            list_finger_table_IDs = list(finger_table.keys()).sort()
            closest_server = list_finger_table_IDs[-1] 
        
        # print(f"    Forwarding the PUT-request to server: {closest_server}...")
        response = requests.put(f"http://{finger_table[closest_server]}/storage/"+key, value)

        # return response.text, response.status_code
        return Response(response.text, status=response.status_code, mimetype='text/plain')         



@app.route("/storage/<key>", methods=["GET"])
def get_data(key):
    print("GET_DATA()")

    #Recieve data
    key = key
    
    print(f"    Key the client want me to retrieve: {key}")

    #Hash the recieved key to find which node it belongs to using SHA-1
    key_ID = hashlib.sha1(key.encode('utf-8')).hexdigest()
    key_ID = int(key_ID, 16)
    key_ID = key_ID % total_IDs

    print(f"    The key_ID is: {key_ID}")


    #This server is responsible for the data
    if(is_ID_in_range(predecessor_ID, my_ID, key_ID) == True):
        print(f"     I am server: {my_ID} and I should have the requested data. checking...")
        
        #Check if key is contained in internal hashtable/dictionary
        if(key in stored_data):
            print(f"    I have the requested data. Returning value to client")
            # return stored_data[key], 200 
            return Response(stored_data[key], status=200, mimetype='text/plain')
            
        else:
            print(f"    The requested data does not exist...")
            # return f"Key not found", 404   
            return Response("Key not found", status=400, mimetype='text/plain')         
        

    #If the key_ID is in the range of my successor
    if(is_ID_in_range(my_ID, successor_ID, key_ID) == True):
        
        #Forward PUT-request to successor server
        print(f"    Forwarding GET-request to server:{successor_ID}...")
        response = requests.get(f"http://{finger_table[successor_ID]}/storage/"+key)

        # return response.text, response.status_code
        return Response(response.text, status=response.status_code, mimetype='text/plain')         



    #If the key is not in range, forward PUT-request to the largest ID in the finger table but still less than the key_ID
    else:
        closest_server = None

        for ID in finger_table:
            if(ID < key_ID):
                closest_server = ID
        
        if(closest_server == None):
            list_finger_table_IDs = list(finger_table.keys()).sort()
            closest_server = list_finger_table_IDs[-1] 
        
        print(f"    Forwarding GET-request to closest server: {closest_server}")
        response = requests.get(f"http://{finger_table[successor_ID]}/storage/"+key)

        # return response.text, response.status_code
        return Response(response.text, status=response.status_code, mimetype='text/plain')         



"""
Returns True if a given key_ID is in the range between a node and its predecessor
Returns False otherwise
"""
def is_ID_in_range(predecessor_ID, node_ID, key_ID):
    if(node_ID == predecessor_ID):
        return True
    
    #If my predecessorID is bigger than myself
    elif(predecessor_ID > node_ID):
        #ranges are from predecessor to maximum node IDs AND from 0 to node_ID
        if((key_ID >= 0 and key_ID <= node_ID) or (key_ID > predecessor_ID and key_ID <= total_IDs)):
            return True
    
    #If my predecessorID is lower than my own ID
    elif(predecessor_ID < node_ID):
        #then ranges are from my own ID down to predecessorID+1
        if(key_ID <= node_ID and key_ID > predecessor_ID):
            return True
    
    #The key_ID is NOT in range
    return False



if __name__ == "__main__":
    print(f"\n########## Code running at server: {HOSTNAME}:{PORT} ##########")
    
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)  #"0.0.0.0" allows all machines to connect to the node
