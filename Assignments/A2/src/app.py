from flask import Flask
import socket
import sys

#Set up Flask application
app = Flask(__name__)

#Get the name of the current node
HOSTNAME = socket.gethostname().split('.')[0]

#Port number given by user
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 5000 #A default port

#Main starting point.
#This code wil be run when someone visits the given url-path
@app.route("/helloworld")
def main():
    #print(f"Started server at {HOSTNAME}:{PORT}")
    return f"{HOSTNAME}:{PORT}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)  #"0.0.0.0" allows all machines to connect to the node