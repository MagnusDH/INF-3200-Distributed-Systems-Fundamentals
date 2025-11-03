# How to run code

1. Navigate into the "src" folder in the terminal
2. Run the following command to compile the "run.sh" script: <br />
    chmod +x run.sh

4. This script automaticly starts the servers and runs the "api-test.py" and "join_experiment.py" files after a few seconds. At the end it proceeds to kill all the processes started on the servers.

5. Run the following command followed by a number to launch the script with n-nodes on the cluster:<br />
    ./run.sh n-nodes
    <br />
    example: "./run.sh 32"
