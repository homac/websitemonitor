"""Check a website and return result dict"""

import re
from datetime import datetime
import requests

import helper

class WebsiteChecker(): # pylint: disable=too-few-public-methods
    """Check a website for it's response time and a potential regexp"""

    def __init__(self, verbose=False):
        self.logger = helper.setup_logging(self.__class__.__name__, verbose)

    def check(self, url, regexp=""):
        """Check a website for it's reponsonse time and a potential regexp

        Args:
            url (str): An URL for the website to check
            regexp (str): A regexp to match on the page's content (defaults to "")

        Returns:
            dict with keys
                'url' (str): The URL that was checked
                'response_code' (int): The HTTP response code
                'response_time' (float): The response time in ms
                'response_result' (bool): If the regexp given matches the content or not
                'timestamp' (str): Timestamp when the request was made (in UTC)
        """

        try:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            resp = requests.get(url)

            regexp = re.compile(regexp)
            matched = False
            if regexp.search(resp.text):
                matched = True

            return {'url': url,
                    'response_code': resp.status_code,
                    'response_time': resp.elapsed.total_seconds(),
                    'response_result': matched,
                    'timestamp': timestamp}

        except requests.ConnectionError:

            self.logger.debug("failed to connect")
            return {'url': url,
                    'response_code': 502,
                    'response_time': 0,
                    'response_result': False,
                    'timestamp': 0}
