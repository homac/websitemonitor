#!/usr/bin/env python3
"""Periodically check a website and post the result to kafka"""

import json
import time
import sys
import signal

from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
from kafka.errors import NoBrokersAvailable

import helper
from website_checker import WebsiteChecker

class Producer():
    """Main producer class to perform a website check and post the result to kafka"""

    def __init__(self, config_file, kafka_config_file, verbose):
        self.logger = helper.setup_logging(self.__class__.__name__, verbose)

        self.producer = None
        self.kafka_params = helper.config(kafka_config_file)
        self.params = helper.config(config_file)
        self.website_checker = WebsiteChecker(verbose)

    def cleanup(self):
        """Flushes and closes the connection"""

        if self.producer:
            self.producer.flush()
            self.producer.close()

    def start_producing(self):
        """Starts to perform the website check at regular intervals, blocks"""

        interval = int(self.params['interval_s'])
        while True:
            self.produce(self.kafka_params['topic'], self.params['url'], self.params['regexp'])
            time.sleep(interval)

    def setup_producer(self):
        """Connects to kafka

        Returns:
            A KafkaProducer object or None
        """

        params = self.kafka_params
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=params['bootstrap_server'],
                security_protocol=params['security_protocol'],
                ssl_cafile=params['ssl_cafile'],
                ssl_certfile=params['ssl_certfile'],
                ssl_keyfile=params['ssl_keyfile']
            )
        except NoBrokersAvailable as exception:
            self.logger.critical("Couldn't connect to kafka service: %s", exception)
            return None

        return self.producer

    def produce(self, topic, url, regexp):
        """Checks the given url and posts a message to kafka

        Args:
            topic (str): The kafka topic to post to. Has to be present on kafka already
            url (str): The URL to check
            regexp (str): A regexp to the the website's content for
        Returns:
            True if message was sent, false otherwise
        """

        self.logger.debug("Checking url %s, %s", url, time.ctime())
        res = self.website_checker.check(url, regexp)

        app_json = json.dumps(res)
        self.logger.debug("Sending: %s", app_json)

        try:
            self.producer.send(topic, app_json.encode('utf-8'))
            self.producer.flush()
            self.logger.debug("flushed")
        except KafkaTimeoutError as exception: # apparently send blocks if the topic isn't there
            self.logger.critical("Sending failed, does the topic %s exist? {%s", topic, exception)
            return False

        return True


if __name__ == "__main__":
    args = helper.parse_cmd_line_args(sys.argv[1:])
    producer = Producer(args.config_file, args.kafka_config_file, args.verbose)

    kafka = producer.setup_producer()
    if not kafka:
        sys.exit(1)

    def signal_handler(*_):
        """Signal handler to catch Ctrl+C key press"""

        print('Ctrl+C pressed, cleaning up...')
        producer.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    producer.start_producing()
