"""Contains the main object for handling database interaction"""

import psycopg2

import helper

class DBConnection():
    """Handle connection and writing of records to PostgresQL database"""

    def __init__(self, verbose=False):
        self.logger = helper.setup_logging(self.__class__.__name__, verbose)
        self.db_connection = None
        self.table_name = None

    def connect(self, params):
        """Connects to the database and sets up the table

        Args:
            params (dict): Connection parameters (host, port, database, user, password)
            table_name: The table to create in the specified database
        Returns:
            pysycopg.connection object or None in case of a failure
        """

        try:
            self.db_connection = psycopg2.connect(host=params['host'],
                                                  port=params['port'],
                                                  database=params['database'],
                                                  user=params['user'],
                                                  password=params['password'])

        except psycopg2.OperationalError as exception:
            self.logger.critical("Couldn't connect to POSTGRES database, is the server up "
                                 "and running? %s", exception)
            return None

        return self.db_connection

    def commit_and_disconnect(self):
        """Commits records to the database and closes the connection"""

        self.db_connection.commit()
        self.db_connection.close()

    def create_table(self, table_name):
        """Create a table

        Args:
            table_name (str): The table to create
        """

        self.table_name = table_name
        stmt = """
            CREATE TABLE IF NOT EXISTS {} (
                    url varchar(2083) NOT NULL,
                    response_code integer NOT NULL,
                    response_time_ms real,
                    response_result boolean,
                    ts timestamp);
            """.format(table_name)

        self.db_connection.cursor().execute(stmt)

    def write_entry(self, url, response_code, response_time, response_result, timestamp):  # pylint: disable=too-many-arguments
        """Write and commit one entry to the database and configured table

        Args:
            url (str): The URL
            response_code (int): The HTTP response code
            response_time (float): The response time in ms
            response_result (bool): True or False depending on the result
        """

        stmt = """
            INSERT INTO {} VALUES ('{}',{},{},{},'{}')
            """.format(self.table_name,
                       url,
                       response_code,
                       response_time,
                       response_result,
                       timestamp)

        self.db_connection.cursor().execute(stmt)
        self.db_connection.commit()
