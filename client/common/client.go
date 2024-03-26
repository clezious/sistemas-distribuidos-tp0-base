package common

import (	
	"net"
	"time"
	"bufio"
	"fmt"
	"os"
	"strings"
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
	BatchSize     int
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
	// open agency-{id}.csv file
	file, err := os.Open(fmt.Sprintf("./data/agency-%v.csv", c.config.ID))
    if err != nil {
		log.Fatalf(
			"action: open_agency_file | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)		
		return
	}
	defer file.Close()
	
	// read file line by line, creating and sending batches
	scanner := bufio.NewScanner(file)	
	batch := ""	
	lineCount := 0
	for scanner.Scan() {		
		select {
			case <-c.shouldStop:
				log.Infof("action: stop_received | result: success | client_id: %v",
					c.config.ID,
				)			
				return
			default:
		}
		if lineCount <= c.config.BatchSize {	
			batch += fmt.Sprintf("%v,%s\n", c.config.ID, scanner.Text())
			lineCount++
		}
		if lineCount == c.config.BatchSize {
			c.sendBatch(batch)
			batch = ""
			lineCount = 0
		}
	}
	if lineCount > 0 {		
		c.sendBatch(batch)
	}
	if err := scanner.Err(); err != nil {
			log.Fatalf(
			"action: read_agency_file | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)		
		return
	}
	// send finished message
	c.sendFinished()		
	// query winners
	retry := true
	for retry {
		retry = c.sendQueryWinners()
		// wait 2 seconds and query again
		time.Sleep(2 * time.Second)		
	}
}

func (c *Client) sendBatch(batch string) {
	c.createClientSocket()
	defer c.stop()
	// Send batch to server
	err := sendClientBatch(c.conn, batch)
	if err != nil {
		log.Fatalf(
			"action: send_client_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)		
		return
	}	
	// Receive server response
	msg, err := recvServerMessage(c.conn)
	if err != nil {
		log.Fatalf(
			"action: recv_server_message | result: fail | error: %v",
			err,
		)		
		return
	} else {
		log.Infof("action: server_response | result: success | client_id: %v | response: %v",
			c.config.ID,
			msg,
		)
		log.Infof("action: apuestas_enviadas | result: success | client_id: %v",
			c.config.ID,
		)
	}		
}

func (c *Client) sendFinished() {
	c.createClientSocket()
	defer c.stop()
	// Send finished message to server
	err := sendClientFinished(c.conn, c.config.ID)
	if err != nil {
		log.Fatalf(
			"action: send_finished_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)		
		return
	}	
	log.Infof("action: send_finished_message | result: success | client_id: %v",
		c.config.ID,
	)
}

func (c *Client) sendQueryWinners() bool{
	c.createClientSocket()
	defer c.stop()
	retry := false
	// Send query to server
	err := sendClientQueryWinners(c.conn, c.config.ID)
	if err != nil {
		log.Fatalf(
			"action: send_query_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)		
		return retry
	}	
	// Receive server response
	// If the query fails, return retry = true
	msg, err := recvServerMessage(c.conn)
	if err != nil {
		log.Fatalf(
			"action: recv_server_message | result: fail | error: %v",
			err,
		)		
		return retry
	}	
	if msg != "QUERY_FAIL\n" {			
		winners := strings.Split(msg, ",")[1]
		log.Infof("action: consulta_ganadores | result: success | client_id: %v | cant_ganadores: %v",
			c.config.ID,
			winners,
		)
	} else {
		retry = true
		log.Infof("action: consulta_ganadores | result: fail | client_id: %v",
			c.config.ID,			
		)
	}

	return retry
}