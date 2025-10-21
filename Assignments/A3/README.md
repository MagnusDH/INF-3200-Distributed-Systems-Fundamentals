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
* The new_node contacts any existing node in the ring (lets call it node_2)
* new_node assigns node_2 as its successor
* node_2 assigns new_node as its predecessor
* when node_2's actuall predecessor (node_1) calls "stabilize()", node_1 asks its successor (node_2) for its predecessor, which is now new_node, then assigns new_node as it successor
* Finaly node_1 notifies new_node about this change, and new_node assigns node_1 as its predecessor 

        nP -> nS
        new_node -> nS
        new_node <- nS

        
        * The old_node finds the successor of new_node
    

        * when an Nth node joins (or leaves) the network, only an  O(1/N) fraction of the keys are moved to a different location
        * In a n-node network, each node maintains information about only O(log N) other nodes, and a lookup requires O(log N) Hashing messages.
    
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

    