"""Unit tests website checker"""

import requests_mock

import sys
sys.path.append("../websitemonitor")
import website_checker

def test_check_website_returns_200():
    with requests_mock.Mocker() as mock:
        mock.register_uri('GET', 'http://test.com', text='resp', status_code=200)

        checker = website_checker.WebsiteChecker()
        test_result = checker.check("http://test.com")

        assert test_result["response_code"] == 200
        assert test_result["response_time"] > 0

def test_check_website_returns_404():
    with requests_mock.Mocker() as mock:
        mock.register_uri('GET', 'http://test.com', text='resp', status_code=404)
        checker = website_checker.WebsiteChecker()
        test_result = checker.check("http://test.com", "ai[abv]en")

        assert test_result["response_code"] == 404
        assert test_result["response_time"] > 0

def test_check_website_url_not_found():

    checker = website_checker.WebsiteChecker()
    test_result = checker.check("http://thisurldoesntexist.not", "ai[abv]en")

    assert test_result["response_code"] == 502
    assert test_result["response_time"] == 0
    assert test_result["response_result"] is False

def test_check_website_regexp_matched():
    with requests_mock.Mocker() as mock:
        mock.register_uri('GET', 'http://test.com', text='resp')
        checker = website_checker.WebsiteChecker()
        test_result = checker.check("http://test.com", "re[abs]p")

        assert test_result["response_result"] is True

def test_check_website_regexp_not_matched():
    with requests_mock.Mocker() as mock:
        mock.register_uri('GET', 'http://test.com', text='resp')
        checker = website_checker.WebsiteChecker()
        test_result = checker.check("http://test.com", "re[abc]p")

    assert test_result["response_result"] is False
