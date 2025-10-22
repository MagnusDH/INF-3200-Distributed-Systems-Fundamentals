import sys
import requests

if len(sys.argv) < 1:
    print("controller.py: missing command line argument")
    sys.exit(1)

#Fetch node from command line argument
list_nodes = sys.argv[1:]

#Make node_0 contact node_1
try:
    response = requests.post(f"http://{list_nodes[0]}/join?nprime={list_nodes[1]}")
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
