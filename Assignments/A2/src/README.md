# How to run code
- Navigate to the /src/ folder in the terminal
- Run the following command to make an executable of the "run.sh" file:
    - "chmod +x run.sh"

- Run the "run.sh" file followed by the number of servers you want to start with this command:
    - "./run.sh 2"



# Server_info layout
- server_info{
    ID : {
        "IP_address" : a IP address string of this node,

        "finger_table" : {
            123 : "ip_address_of_node_123"
            456 : "ip_address_of_node_456"
        },

        "predecessor" : integer ID of predecessor node
    }

    21: {'IP_address': 'c7-16:52057', 'finger_table': {115: 'c7-4:61910', 207: 'c11-11:54656'}, 'predecessor': 207}, 115: {'IP_address': 'c7-4:61910', 'finger_table': {147: 'c6-11:64379', 207: 'c11-11:54656', 21: 'c7-16:52057'}, 'predecessor': 21}
}