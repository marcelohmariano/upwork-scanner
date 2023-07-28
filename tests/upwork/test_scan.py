import os.path

import pytest

from upwork import browser
from upwork import scan


@pytest.fixture
def data_directory() -> str:
    return '/data'


@pytest.fixture
def driver() -> browser.Driver:
    driver = browser.Driver(selenium_server_url='http://localhost:4444',
                            selenium_wait_timeout=60.0)
    yield driver
    driver.quit()


def test_job_matches_extractor(driver: browser.Driver, data_directory: str):
    url = os.path.join(data_directory, 'main_page.mht')
    driver.load(f'file://{url}')

    job_matches_extractor = scan.JobMatchesExtractor(driver)
    matches = job_matches_extractor.extract_job_matches()

    assert len(matches) == 30
    for match in matches:
        assert match.job_title != ''
        assert match.job_description != ''


def test_user_data_extractor(driver: browser.Driver, data_directory: str):
    url = os.path.join(data_directory, 'main_page.mht')
    driver.load(f'file://{url}')

    url = os.path.join(data_directory, 'contact_info_page.mht')
    url = f'file://{url}'

    user_data_extractor = scan.UserDataExtractor(driver=driver,
                                                 secret_answer='test',
                                                 contact_info_url=url)
    user_data = user_data_extractor.extract_user_data()

    assert user_data.user_id == '1941e405'
    assert user_data.user_name == 'Dave Worker'
    assert user_data.email == 'r******sk@argyle.com'
    assert user_data.job_title == 'Software engineer'


def test_address_data_extractor(driver: browser.Driver, data_directory: str):
    url = os.path.join(data_directory, 'tax_info_page.mht')
    url = f'file://{url}'

    address_data_extractor = scan.AddressDataExtractor(driver=driver,
                                                       tax_info_url=url)
    address_data = address_data_extractor.extract_address_data()

    assert address_data.line1 == 'Milk Ave 64'
    assert address_data.line2 == ''
    assert address_data.city == 'Boston'
    assert address_data.state == 'MA'
    assert address_data.postal_code == '02145'
    assert address_data.country == 'United States'
