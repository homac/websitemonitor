"""Unit tests for DB interaction"""

import pytest
from psycopg2.errors import UndefinedTable
from datetime import datetime
import sys
sys.path.append("../websitemonitor")

import db

def test_check_table_is_created(postgresql):
    """Checks if the required table for data storage has been created"""
    conn = db.DBConnection()
    conn.db_connection = postgresql

    table_name = "test"
    conn.create_table(table_name)

    stmt = """
            SELECT * FROM {};
            """.format(table_name)

    try:
        postgresql.cursor().execute(stmt)
    except UndefinedTable:
        pytest.fail("Expected table has not been created")

    conn.commit_and_disconnect()

def test_check_write_entry(postgresql):
    """Check if writing to DB is succesful"""
    cursor = postgresql.cursor()
    conn = db.DBConnection()
    conn.db_connection = postgresql

    table_name = "test"
    conn.create_table(table_name)

    url = "http://test.com"
    response_code = 200
    response_time = 0.123
    response_result = True
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    conn.write_entry(url, response_code, response_time, response_result, timestamp)

    stmt = """
            SELECT * FROM {};
            """.format(table_name)

    cursor.execute(stmt)
    result = cursor.fetchone()

    assert result[0] == url
    assert result[1] == response_code
    assert result[2] == response_time
    assert result[3] == response_result
    assert str(result[4]) == timestamp
