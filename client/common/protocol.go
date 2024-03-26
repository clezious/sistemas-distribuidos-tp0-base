package common

import (	
	"fmt"
	"net"	
	"bufio"	
)

func sendClientBatch(conn net.Conn, batch string) error {
	// Sends a batch of bets to the server
	// in the format: 
	// BATCH_START\n
	// ID,NOMBRE,APELLIDO,DOCUMENTO,NACIMIENTO,NUMERO\n
	// ...
	// BATCH_END\n	
	msg := fmt.Sprintf(
		"BATCH_START\n%sBATCH_END\n",
		batch,
	)
	msgLen := len(msg)	
	bytesWritten := 0
	for bytesWritten < msgLen {
		n, err := fmt.Fprintf(conn, msg)
		if err != nil {
			return err
		} else {
			bytesWritten += n
		}
	}
	return nil
}

func sendClientFinished(conn net.Conn, clientId string) error {
	// Sends a message to the server indicating that the client has finished sending bets
	_, err := fmt.Fprintf(conn, "FINISHED,%v\n", clientId)
	return err
}

func sendClientQueryWinners(conn net.Conn, clientId string) error {
	// Sends a query to check the quantity of the winning bets from this agency
	_, err := fmt.Fprintf(conn, "QUERY,%v\n", clientId)
	return err
}

func recvServerMessage(conn net.Conn) (string, error) {
	msg, err := bufio.NewReader(conn).ReadString('\n')	
	return msg, err
}