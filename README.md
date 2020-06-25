## Website monitoring via kafka and SQL database

Websitemonitor is a simple project that monitors availability of a website and stores the result into a PostgreSQL database. 

It comprises of two parts:

  1. The producer tries to fetch a website at regular intervals, and posts the result including HTTP response code and response time to a kafka topic. 

  2. The consumer listens for messages on that kafka topic and writes the content of that message to a PostgrSQL database.

Both tools can be configured and ran independently.

Disclaimer: Before running the tools, both a kafka and postgresql service must already be running. Also the kafka topic that is used has to exist on the kafka service.

### Usage

#### Configuration
Configure the interface to kafka (kafka.ini), the producer (poducer.ini) and the consumer (consumer.ini). For kafka, the same config file can be used. You also need ssl certificates for access to the kafka service and configure their location in the kafka config file. Templates can be found in the config/ directory.

Then initialize the python environment:

```console
$ make init
```

#### Run the producer
```console
$ ./websitemonitor/producer.py --kafka-config-file ./config/kafka.ini --config-file ./config/producer.ini
```

#### Run the consumer:

```console
$ ./websitemonitor/consumer.py --kafka-config-file ./config/kafka.ini --config-file ./config/consumer.ini
```

## Testing

Run the unit tests with
```console
$ make test
```

This also runs the linter which can be executed individually by
```console
$ make lint
```

## Docker

For ease of deployment and integration into CI systems, a simple Dockerfile that can run both the producer and the consumer independently is supplied.

Build the docker image with:

```console
$ make docker
```

Put your ssl cert and key files into /path/to/configuration/dir (see below) and use a kafka.ini similar to this:
```
[DEFAULT]
bootstrap_server = kafka-1801c7d9-homac-409a.aivencloud.com:20636
security_protocol = SSL
ssl_cafile = /app/config/ca.pem
ssl_certfile = /app/config/service.cert
ssl_keyfile = /app/config/service.key
topic = testtopic
```

Then run the tools with:

#### Consumer
```console
docker run -v /path/to/configuration/dir:/app/config/ -t --rm websitemonitor /app/websitemonitor/consumer.py \
            --kafka-config-file /app/config/kafka.ini \
            --config-file /app/config/consumer.ini
```

#### Producer
```console
docker run -v $/path/to/configuration/dir:/app/config/ -t --rm websitemonitor /app/websitemonitor/producer.py \
            --kafka-config-file /app/config/kafka.ini \
            --config-file /app/config/producer.ini
```

Replace the /path/to/your/configuration to the path where your actual configuration (and ssl certification) can be found.

## Database schema

The database schema that is used for the Postgresql database is:

```sql
    CREATE TABLE IF NOT EXISTS website_stats (
                url varchar(2083) NOT NULL,
                response_code integer NOT NULL,
                response_time_ms real,
                response_result boolean,
                ts timestamp);
```

The table name can be configured in the config file consumer.ini.

## TODOs

There's definitely some room for more unit testing.
