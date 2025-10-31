# To run code
* Api-skeleton.py is the file I am implementing node logic in
* api-test.py sends HTTP requests to my node testing each function. A node IP:address is required when running this file
* join_experiment.py requires a list of nodes IP:addresses

# Program flow
* start a server at a node
* run api-test.py to perform tests on the started node
* 



# Chord protocol

## What variables each node must store:
* Successor: next node in the ring
* Predecessor: previous node in the ring
* successor_list[]: list of 3-5 entries with IDs of the next nodes in the ring
* Finger table: list of node IDs with given steps ahead for faster lookups
* Stored_Data{}: dictionary with key-value pairs for storage of data

## How keys are stored and retrieved:
* Each node has an m-bit identifier that is created by hashing their IP:address using SHA-1
* Keys are hashed and stored at nodes with the same number or lower just next to the predecessor. So if nodes 1, 5, 10 exists, then keys 2,3,4,5 will be stored at node 5. Keys 11,12,13,1 will be stored at node 1
* If a retrieve/store request for a key is forwarded to a node that does not respond, then another node should be tried (for example the next entry in the successor_list or another close entry in the finger table) 

## How a new node joins the network:
* The new_node contacts any existing node in the ring (lets call it node_2) and provides its ID and IP:address
* node_2 makes checks to find out who should be the successor of new_node:
    * node_2 is the successor of new_node
        * node_2 tells new_node that node_2 is the successor
        * node_2 gives its successor list to new_node
        * node_2 tells new_node who node_2s predecessor was
        * node_2 updated its predecessor to new_node    
        
        * new_node assigns node_2 as its successor
        * new_node recieves the successor list of node_2 and updates its successor list
        * new_node assigns node_2s predecessor as its predecessor
    
    * is new_node the successor of node_2?
        * node_2 tells new_node that node_2 is its predecessor
        * node_2 gives its successor list to new_node
        * node_2 assigns new_node as its successor and updates its successor list
        * new_node recieves successor list from node_2 and updates its successor list
        * new_node assigns node_2 as its predecessor

    
    * node_2 does not know the successor
        * forward the reqest to closest node responsible for new_node->ID

    * new_node calls stabilize at the end?


<!-- * new_node assigns node_2 as its successor
* node_2 assigns new_node as its predecessor
* when node_2's actuall predecessor (node_1) calls "stabilize()", node_1 asks its successor (node_2) for its predecessor, which is now new_node, then assigns new_node as it successor
* Finaly node_1 notifies new_node about this change, and new_node assigns node_1 as its predecessor 

        nP -> nS
        new_node -> nS
        new_node <- nS -->

    
## How a node leaves the network:
* Current_node sends to its successor:
    * its keys
    * its predecessor_node
    
* Current_node sends to its predecessor:
    * its successor_list

* Current_node->successor will:
    * Add keys to its storage (not necessary in this assignment)
    * Remove its predecessor node and replace it with current_nodes->predecessor

* current_node->predecessor will:
    * Remove current_node from its successor_list and add the last entry from current_node->successor_list to its own successor list as the last entry


## How the network stabilizes itself: 
* Every node must run "stabilize()" every few seconds: 
    * Each node asks its successor for the successor's predecessor and decides if the predecessor should be the current node's successor instead
    * Notify the current node's successor of its own existence, giving the successor the chance to change its predecessor to the current_node
    * Call "fix_fingers()" to make sure the entries in its finger table are correct:
        * HOW?
* Call "check_predecessor()" to clear the current_nodes predecessor if the predecessor has failed. This allows it to accept a new predecessor
            
* Update successor_list:
    * if the current_node's successor is alive:
        * Current_node asks its successor for its successor list
        * Current_node places its successor in the first index in the list, and shifts the other nodes to the right effectively removing the last entry
    * if the current_node's successor is dead:
        * Current_node promotes the next node in the successor list as its new successor
        * Current_node asks its new successor for its successor list
        * Current_node places its successor in the first index in the list, and shifts the other nodes to the right effectively removing the last entry

## How the network recovers from failure:
* Each node keep a list of possible successors. This was if the first successor does not respond, then the next successor in the list can be appointed its successor.
    * list_successors[s1, s2, s3, ...sN]
    * Each entry in the list is the successor of each successor, so s1 is the successor of this node. s2 is the successor of s1 and so on. 

    

# TESTS

## Time to grow network
* 2 nodes: 0.05, 0.04, 0.04
* 4 nodes: 2.13, 2.13, 2.14 
* 8 nodes: 12.43, 8.41, 8.43
* 16 nodes: 11.18, 6.92, 9.01
* 32 nodes: 25.42, 14.51, 18.93

## Time to become stable after shrinking
* 4 -> 2 : 0.02, 0.03, 0.03
* 8 -> 4 : 2.07, 0.05, 2.07
* 16 -> 8 : 2.13, 2.13, 0.11
* 32 -> 16 : 2.25, 2.25, 2.26

## Become stable after crashes:
* 1 crash: 1.11 seconds to become stable again
* 2 crash: 2.03 seconds to become stable again
* 3 crash: 5.20
* 4 crash: 6.19
* 5 crash: 5.11
* 6 crash: 10.28
* 7 crash: 7.12
* 8 crash: 8.12
* 9 crash: 9.12
* 10 crash: 10.12
* 11 crash:
* 12 crash:
* 13 crash:
* 14 crash:
* 15 crash:
* 16 crash:
* 17 crash:
* 18 crash:
* 19 crash:
* 20 crash:
* 21 crash:
* 22 crash:
* 23 crash:
* 24 crash:
* 25 crash:
* 26 crash:
* 27 crash:
* 28 crash:
* 29 crash:
* 30 crash:
* 31 crash:

