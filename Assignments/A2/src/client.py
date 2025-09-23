import requests
import sys
import json
import socket



#Fetch server name+port ad convert them to a list 
server_to_contact = sys.argv[1]

#Fetch IP address of client
client_IP_address = socket.gethostbyname(socket.gethostname())


def PUT_data(data_to_put, server_address):
    #Try to contact server and put data into the system
    try:
        response = requests.post(f"http://{server_to_contact}/put", json=data_to_put)
        # print(f"client.py: received message from {server_to_contact}: {response.text}")

    except Exception as e:
        print(f"client.py: request sent to {server_to_contact} failed. ERROR: {e}\n")


def GET_data(requested_data, server_address):
    print("GET_DATA()")
    # try:
    #     print(f"\nclient.py: sending GET-request to server:{server_address}...")
    #     recieved_data = requests.get(f"http://{server_address}/get")
    #     print(f"client.py: received data from {server_address}: {recieved_data.text}")

    #     if recieved_data.status_code == 200:
    #         print(f"Value for '{requested_data}': {recieved_data.text}")
    #     else:
    #         print(f"Key '{requested_data}' not found. Status code: {recieved_data.status_code}")


    # except Exception as e:
    #     print(f"client.py: GET-request sent to {server_address} failed. ERROR: {e}\n")



if __name__ == "__main__":
    print("\n########### Client.py ###########\n")

    #create some data to send
    data_to_put = {
        "data": ["apple", "banana"],
        "client_IP": client_IP_address
    }

    print("client.py: Trying to put data to put into system")
    #try to put data in system
    PUT_data(data_to_put, server_to_contact)

    import time
    time.sleep(2)

    #Try to retrieve data
    print("client.py: Trying to retrieve data from system")
    key_to_retrieve = "apple"
    retrieved_data = get_data(key_to_retrieve, server_to_contact)