package common

import (	
	"fmt"
	"net"	
	"bufio"
)

func sendClientMessage(conn net.Conn, ID string, NOMBRE string,
						APELLIDO string,DOCUMENTO string,
					   	NACIMIENTO string,NUMERO string) error {
	// Sends bet information to the server
	// in the format: ID|NOMBRE|APELLIDO|DOCUMENTO|NACIMIENTO|NUMERO
	// With a newline character at the end
	msg := fmt.Sprintf(		
		"%v|%v|%v|%v|%v|%v\n",
		ID,
		NOMBRE,
		APELLIDO,
		DOCUMENTO,
		NACIMIENTO,
		NUMERO,			
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

func recvServerMessage(conn net.Conn) (string, error) {
	msg, err := bufio.NewReader(conn).ReadString('\n')
	return msg, err
}