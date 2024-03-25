package common

import (	
	"net"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
	NOMBRE        string
	APELLIDO      string
	DOCUMENTO     string
	NACIMIENTO    string
	NUMERO        string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	shouldStop chan bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, shouldStop chan bool) *Client {
	client := &Client{
		config: config,
		shouldStop: shouldStop,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}
func (c *Client) stop() {
	c.conn.Close()	
	log.Infof("action: shutting_down_socket | result: success | client_id: %v",
		c.config.ID,
	)
}

func (c *Client) StartClientLoop() {			
	select {
		case <-c.shouldStop:
			log.Infof("action: stop_received | result: success | client_id: %v",
				c.config.ID,
			)
			c.stop()
			return
		default:
	}
			
	c.createClientSocket()

	err := sendClientMessage(c.conn, c.config.ID, c.config.NOMBRE, c.config.APELLIDO, c.config.DOCUMENTO, c.config.NACIMIENTO, c.config.NUMERO)
	if err != nil {
		log.Fatalf(
			"action: send_client_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		c.stop()
		return
	}
	msg, err := recvServerMessage(c.conn)
	if err != nil {
		log.Fatalf(
			"action: recv_server_message | result: fail | error: %v",
			err,
		)
		c.stop()
		return
	} else {
		log.Infof("action: server_response | result: success | client_id: %v | response: %v",
			c.config.ID,
			msg,
		)
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			c.config.DOCUMENTO,
			c.config.NUMERO,
		)
	}
	
	c.stop()
}
