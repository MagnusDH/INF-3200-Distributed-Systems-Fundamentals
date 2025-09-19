from flask import Flask, request
import socket
import sys

# Silence werkzeug logs
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

#Set up Flask application
app = Flask(__name__)

#Get the name of the current node
HOSTNAME = socket.gethostname().split('.')[0]

Server_ID = None
finger_table = None

#Port number given by user
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 5000 #A default port


#the data that is stored in this server
stored_data = {}


#This code wil be run when someone visits the given url-path
@app.route("/")
def home():
    return f"This is server: {ID} running at: {HOSTNAME}:{PORT}"


@app.route("/initialize", methods=["POST"])
def initialize_server():
    #Recieve data
    recieved_data = request.get_json() 
    
    #Unpack data
    ID = recieved_data.get("ID")
    finger_table = recieved_data.get("finger_table")

    #Set values
    server_ID = ID
    finger_table = finger_table

    return f"{HOSTNAME}:{PORT}: I recieved the payload: ID:{ID}, finger_table:{finger_table}.", 200


@app.route("/put", methods=["POST"])
def put_data():

    #Recieve data
    recieved_data = request.get_json()
    key = list(recieved_data.keys())[0]
    value = recieved_data[key]
    
    #Store the clients IP_address
    client_IP_address = request.remote_addr


    #HASH TKE HEY USING SHA-1
    #Convert the key to bytes
    bytes_key = key.encode()
    #Hash the key using SHA-1
    hashed_key = hashlib.sha1(bytes_key)
    #Convert the hashed key into a hexadecimal string
    hash_hex = hashed_key.hexdigest()
    #Convert the hexadecimal string to integer
    hash_int = int(hash_hex, 16)

    #Convert hash value into a server_ID
    responsible_server = hash_int % total_IDs


    #FIND SERVER THAT IS RESPONSIBLE FOR THE DATA
    #This server is responsible for saving the data
    if(server_ID == responsible_server):
        stored_data[key] = value

        #send return message to client
        return f"{HOSTNAME}:{PORT}: I stored the data: {recieved_data}", 200


    #Another server is responsible to save the data
    else:
        #if the responsible server is contained in the finger table
        if(responsible_server in finger_table):
            try:
                print(f"\n{HOSTNAME}:{PORT}: I can not store the data, but I know the node that can. Forwarding it to server:{responsible_server}")

                response = requests.post(f"http://{finger_table[responsible_server]}/put", json=recieved_data)
                print(f"{HOSTNAME}:{PORT}: received message from server:{server_to_contact}: {response.text}")

            except Exception as e:
                print(f"{HOSTNAME}:{PORT}: request sent to server:{server_to_contact} failed. ERROR: {e}\n")
        
        #The responsible server is not in the finger table
        else:
            #find the ID in the finger table that is closest to the actuall server
            closest_server = 0
            for ID in finger_table:
                if(ID <= responsible_server):
                    closest_server = ID

        #forward the original message
        print(f"\n{HOSTNAME}:{PORT}: I can not store the data. forwarding it to closest server:{closest_server}")

        response = requests.post(f"http://{finger_table[closest_server]}/put", json=recieved_data)
        print(f"{HOSTNAME}:{PORT}: received message from closest server:{server_to_contact}: {response.text}")

    return f"{HOSTNAME}:{PORT}: The client wants to put this data into the system: {recieved_data}...", 200


@app.route("/get", methods=["GET"])
def get_data():

    return f"{HOSTNAME}:{PORT}: Some client wants to get data from me. Trying..."


# def forward_request(key, data):
#     pass

    

if __name__ == "__main__":

    print(f"\n########## Code running at server: {HOSTNAME}:{PORT} ##########")
    
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)  #"0.0.0.0" allows all machines to connect to the node
