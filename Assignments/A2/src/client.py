import requests
import sys
import json
import socket
import time


#Fetch server name+port ad convert them to a list 
server_to_contact = sys.argv[1]

#Fetch IP address of client
client_IP_address = socket.gethostbyname(socket.gethostname())


def PUT_data(data_to_put, server_address):
    #Try to contact server and put data into the system
    try:
        response = requests.post(f"http://{server_to_contact}/put", json=data_to_put)
        # print(f"client.py: received message from {server_to_contact}: {response.text}")
        return response

    except Exception as e:
        print(f"client.py: request sent to {server_to_contact} failed. ERROR: {e}\n")


def GET_data(request_data, server_address):
    # print("\nGET_DATA()")
    try:
        # print(f"\nclient.py: sending GET-request to server:{server_address}...")
        response = requests.get(f"http://{server_address}/get?key={request_data}")
        # print(f"client.py: received data from {server_address}: {response.text}")

        return response

    except Exception as e:
        print(f"client.py: GET-request sent to {server_address} failed. ERROR: {e}\n")



if __name__ == "__main__":
    print("\n########### Client.py ###########\n")

    response = requests.get(f"http://{server_to_contact}/network")

    print(response.text)




    # print("    Putting 100 values into system")
    # time.sleep(2)
    # #create some data to send and request
    # for i in range(100):
    #     data_to_put = {
    #         "data": [str(i), str(i*10)]
    #     }

    #     response = PUT_data(data_to_put, server_to_contact)
    #     print("    response.text = ", response.text)

    # time.sleep(2)

    # #Retrieve data
    # print(f"\n    Retrieving 100 values from system")
    # time.sleep(2)

    # for i in range(100):
    #     #Generate key
    #     key_to_retrieve = str(i)

    #     #request key
    #     # print("    requesting key:", key_to_retrieve)
        
    #     response = GET_data(key_to_retrieve, server_to_contact)

    #     print("    retrieved value: ", response.text)

    #     # print(f"    Retrieved data = {response.text}")