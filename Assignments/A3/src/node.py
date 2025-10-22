from flask import Flask, request, jsonify
import requests
import sys
import hashlib

app = Flask(__name__)

# Silence werkzeug logs
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

#Internal info
storage = {}
node_ID = None
node_hash = None
successors = []
predecessor = None
finger_table = {}
crashed = False

#Total number of IDs in chord ring
m = 10
ring_size = 2**m

def create_ID_and_hash(IP_address):
    #Create hash value for current server using SHA-1
    hash_object = hashlib.sha1(IP_address.encode())  # encode string to bytes
    hash_hex = hash_object.hexdigest()      # hexadecimal string
    hash_int = int(hash_hex, 16)            # convert hex to integer

    #Convert hash value into a server_ID
    ID = hash_int % ring_size
    
    return int(ID), hash_hex


@app.route('/storage/<key>', methods=['GET'])
def handle_get(key):
    val = storage.get(key, None)
    if val is None:
        return "Not Found", 404, {"Content-type": "text/plain"}
    else:
        return val, 200, {"Content-type": "text/plain"}


@app.route('/storage/<key>', methods=['PUT'])
def handle_storage_put(key):
    data = request.get_data(as_text=True)
    storage[key] = data
    return "OK", 200, {"Content-type": "text/plain"}


#DONE
@app.route('/node-info', methods=['GET'])
def handle_node_info():
    info = {
        "node_hash": node_hash,
        "successor": successors,
        "others": finger_table
    }
    return jsonify(info), 200, {"Content-type": "application/json"}


@app.route('/leave', methods=['POST'])
def handle_leave():
    return "OK", 200, {"Content-type": "text/plain"}


@app.route('/sim-crash', methods=['POST'])
def handle_sim_crash():
    return "OK", 200, {"Content-type": "text/plain"}


@app.route('/sim-recover', methods=['POST'])
def handle_sim_recover():
    return "OK", 200, {"Content-type": "text/plain"}


"""
-initiates this node to join an existing network
-A request is sent to this node with an existing ring node as argument
-
"""
@app.route('/join', methods=['POST'])
def join_ring():
    print("\nHANDLE_JOIN()")

    existing_node = request.args.get('nprime')

    #Contact existing_node
    print(f"    Contacting {existing_node} to join network...")
    response = requests.post(f"http://{existing_node}/help_join")


    #Assign existing_node as my successor
    #

    """
    * The new_node contacts any existing node in the ring (lets call it node_2)
    * new_node assigns node_2 as its successor
    * node_2 assigns new_node as its predecessor
    * when node_2's actuall predecessor (node_1) calls "stabilize()", node_1 asks its successor (node_2) for its predecessor, which is now new_node, then assigns new_node as it successor
    * Finaly node_1 notifies new_node about this change, and new_node assigns node_1 as its predecessor


    """

    return "OK", 200, {"Content-type": "text/plain"}

@app.route('/help_join', methods=['POST'])
def help_join():
    print("\nHELP_JOIN()")

    return "OK", 200



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Missing argument: <host:port>")
        sys.exit(1)
    
    host, port = sys.argv[1].split(':')
    node_ID, node_hash = create_ID_and_hash(f"{host}:{port}")
    
    print(f"Server: {host}:{port}")    
    print(f"Node ID: {node_ID}")
    print(f"Node hash: {node_hash}")


    successors = []
    predecessor = None
    finger_table = {}

    app.run(host=host, port=int(port))
