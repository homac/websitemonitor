#!/usr/bin/env python3
"""Consume message from kafka and write to PostgeSQL database"""

import json
import sys
import time
import signal

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

import helper
from db import DBConnection

class Consumer():
    """Main object to consume messages from kafak and write the to a PostgreSQL database"""

    def __init__(self, config_file, kafka_config_file, verbose):
        self.logger = helper.setup_logging(self.__class__.__name__, verbose)

        self.db_connection = DBConnection(verbose)
        self.kafka_consumer = None

        self.kafka_params = helper.config(kafka_config_file)
        self.db_params = helper.config(config_file, "db")
        self.params = helper.config(config_file)

    def start_consuming(self):
        """Periodically checks kafka for new messages, blocks"""

        interval = int(self.params['interval_s'])
        while True:
            self.consume()
            time.sleep(interval)

    def cleanup(self):
        """Disconnects from kafka, commits and closes the connection to the database"""

        if self.kafka_consumer:
            self.kafka_consumer.close()
        if self.db_connection:
            self.db_connection.commit_and_disconnect()

    def setup_db(self):
        """Sets up the connection to the database

        Returns:
            False if something goes wrong, True otherwise
        """
        conn = self.db_connection.connect(self.db_params)

        if not conn:
            return False

        self.db_connection.create_table(self.db_params['table_name'])

        return True

    def setup_consumer(self):
        """Sets up the kafka consumer

        Returns:
            False if something goes wrong, True otherwise
        """

        params = self.kafka_params
        try:
            self.kafka_consumer = KafkaConsumer(
                self.kafka_params['topic'],
                auto_offset_reset="earliest",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                bootstrap_servers=params['bootstrap_server'],
                client_id=self.params['kafka_client_id'],
                group_id=self.params['kafka_group_id'],
                security_protocol=params['security_protocol'],
                ssl_cafile=params['ssl_cafile'],
                ssl_certfile=params['ssl_certfile'],
                ssl_keyfile=params['ssl_keyfile'],
            )
        except NoBrokersAvailable as exception:
            self.logger.critical("Couldn't connect to kafka service: %s", exception)
            return None

        return True

    def consume(self):
        """Consumes all pending messages from kafka and writes them to the database"""

        self.logger.debug("Checking for new messages %s", time.ctime())
        raw_msgs = self.kafka_consumer.poll(timeout_ms=1000)
        for _, msgs in raw_msgs.items():
            for msg in msgs:
                self.logger.debug("Received and writing: %s", msg.value)

                self.db_connection.write_entry(msg.value['url'],
                                               msg.value['response_code'],
                                               msg.value['response_time'],
                                               msg.value['response_result'],
                                               msg.value['timestamp'])

                # Commit offsets so we won't get the same messages again
                self.kafka_consumer.commit()

if __name__ == "__main__":
    args = helper.parse_cmd_line_args(sys.argv[1:])
    consumer = Consumer(args.config_file, args.kafka_config_file, args.verbose)

    kafka = consumer.setup_consumer()
    if not kafka:
        sys.exit(1)

    if not consumer.setup_db():
        consumer.cleanup()
        sys.exit(1)

    def signal_handler(*_):
        """Signal handler to catch Ctrl+C key press"""

        print('Ctrl+C! pressed, cleaning up...')
        consumer.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    consumer.start_consuming()
