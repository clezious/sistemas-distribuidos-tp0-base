#!/bin/sh

SERVER="server"
PORT=12345
MESSAGE="Hello, world!"

# Send the message to the server using netcat
# Read the received message
echo "Sending message to server: $MESSAGE"
RECEIVED=$(echo -n "$MESSAGE" | nc $SERVER $PORT)
echo "Received message from server: $RECEIVED"

# Compare the sent and received messages
if [ "$MESSAGE" = "$RECEIVED" ]; then
    echo "Test passed: Sent and received messages are the same."
    exit 0
else
    echo "Test failed: Sent and received messages are different."
    exit 1
fi
