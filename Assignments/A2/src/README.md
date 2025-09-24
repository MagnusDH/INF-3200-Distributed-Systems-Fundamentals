# How to run code
- Navigate to the /src/ folder in the terminal

- Run the following command to make an executable of the "run.sh" file:
    - "chmod +x run.sh"

- Run the "run.sh" file followed by the number of servers you want to start with this command:
    - "./run.sh 2"
    

# To run chord-tester.py
    - run the code as mentioned above

    - The client.py file will print a list of available nodes for one specific server
    
    - Copy the printed string.
        - example print: "List of available nodes from c10-1:55952:  ["c7-2:64697"]"

    -run the following command to run the chord tester along with the printed server IP-address
        - python3 chord-tester.py 'c7-2:64697'