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
    # print("\n########### Client.py ###########\n")

    #Get list of nodes for a server
    response = requests.get(f"http://{server_to_contact}/network")

    print(f"List of available nodes from {server_to_contact}: ", response.text)

    #Put value into system
    print("Putting 100 values into system...\n")
    time.sleep(1)
    successfull_puts = []

    #Start measuring PUT time
    start_time_put = time.time()

    for i in range(100):
        key = str(i)
        value = str(i*10)

        response = requests.put(f"http://{server_to_contact}/storage/"+key, value)

        if(response.status_code == 200):
            successfull_puts.append(value)
    
    #Stop PUT time
    end_time_put = time.time()

    #Measure total time used for put operations
    total_time_put = end_time_put - start_time_put
    put_throughput = 100 / total_time_put


    #Retrieve value from system
    # time.sleep(2)
    # print("\nTrying to retrieve 100 values from system...\n")
    successfull_gets = []
    #Start measuring PUT time
    start_time_get = time.time()
    for i in range(100):
        key = str(i)
        response = requests.get(f"http://{server_to_contact}/storage/"+key)
        
        if(response.status_code == 200):
            successfull_gets.append(response.text)
    
    #Stop PUT time
    end_time_get = time.time()

    #Calculate used time
    total_time_get = end_time_get - start_time_get
    get_throughput = 100 / total_time_get

    print(f"\nSuccessfully put: {len(successfull_puts)} values into the system")
    print(f"Values in system: {successfull_puts}\n")
    print(f"\nSuccessfully retrieved: {len(successfull_gets)} from system")
    print(f"Retrieved values: {successfull_gets}")
    
    print(f"\nTime used put: {total_time_put}")
    print(f"\nTime used get: {total_time_get}")