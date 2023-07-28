import contextlib
import time
from typing import Generator

import pydantic
from selenium.common import NoSuchElementException, TimeoutException

from upwork import browser
from upwork import log
from upwork.browser import By, wait

_LOGIN_URL = 'https://www.upwork.com/ab/account-security/login'
_CONTACT_INFO_URL = 'https://www.upwork.com/freelancers/settings/contactInfo'
_TAX_INFO_URL = 'https://www.upwork.com/nx/tax/'


class Credentials(pydantic.BaseModel):
    username: str
    password: str
    secret_answer: str


class UserData(pydantic.BaseModel):
    user_id: str
    user_name: str
    email: str
    job_title: str


class AddressData(pydantic.BaseModel):
    line1: str
    line2: str
    city: str
    state: str
    postal_code: str
    country: str


class JobMatch(pydantic.BaseModel):
    job_title: str
    job_description: str


class Result(pydantic.BaseModel):
    user: UserData
    address: AddressData
    job_matches: list[JobMatch]

    def save(self, filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))


class Actor:
    def __init__(self, driver: browser.Driver):
        self.driver = driver


class JobMatchesExtractor(Actor):
    _JOB_SECTION_CSS = '.up-card-section.up-card-list-section.up-card-hover'
    _JOB_SECTION_SIBLING_XPATH = _JOB_SECTION_CSS.replace('.', ' ').strip()

    def _job_sections(self) -> Generator[browser.WebElement, None, None]:
        self.driver.wait(wait.presence_of_all_elements_located((
            By.CSS_SELECTOR, self._JOB_SECTION_CSS
        )))

        sections = self.driver.find_elements_by_css(self._JOB_SECTION_CSS)
        section = sections[0]

        while True:
            yield section

            self.driver.execute_script('arguments[0].scrollIntoView()',
                                       section)

            time.sleep(0.5)

            with contextlib.suppress(NoSuchElementException):
                section = section.find_element(
                    By.XPATH,
                    f'following-sibling::'
                    f'section[@class="{self._JOB_SECTION_SIBLING_XPATH}"][1]'

                )
                continue

            break

    def extract_job_matches(self) -> list[JobMatch]:
        matches = []

        for section in self._job_sections():
            job_title_label = section.find_element(By.CLASS_NAME,
                                                   'job-tile-title')

            job_title = job_title_label.text.strip()
            job_description = section.text.replace(job_title_label.text,
                                                   '').strip()

            match = JobMatch(job_title=job_title,
                             job_description=job_description)
            matches.append(match)

        return matches


class Authenticator(Actor):
    def __init__(self, driver: browser.Driver, credentials: Credentials):
        super().__init__(driver)
        self._credentials = credentials

    def _send_user(self) -> None:
        self.driver.load(_LOGIN_URL)
        self.driver.set_input_text(
            'login_username', self._credentials.username
        )
        self.driver.click_button('login_password_continue')

    def _send_password(self) -> None:
        self.driver.set_input_text(
            'login_password', self._credentials.password
        )
        self.driver.click_button('login_control_continue')

    def _send_secret_answer(self) -> None:
        self.driver.set_input_text(
            'login_answer', self._credentials.secret_answer
        )
        self.driver.click_button('login_control_continue')

    def authenticate(self) -> None:
        self._send_user()
        self._send_password()

        if self._is_logged_in():
            return

        self._send_secret_answer()

    def _is_logged_in(self) -> bool:
        def condition(_):
            with contextlib.suppress(NoSuchElementException):
                return self.driver.find_element_by_id('login_answer')

            return self.driver.find_element_by_id('fwh-sidebar-profile')

        element = self.driver.wait(condition)
        return element.get_attribute('id') == 'fwh-sidebar-profile'


class UserDataExtractor(Actor):
    def __init__(
        self,
        driver: browser.Driver,
        secret_answer: str,
        contact_info_url: str = _CONTACT_INFO_URL
    ):
        super().__init__(driver)
        self._secret_answer = secret_answer
        self._contact_info_url = contact_info_url

    def _asked_for_secret_answer(self) -> bool:
        with contextlib.suppress(TimeoutException):
            self.driver.wait(
                condition=wait.presence_of_element_located((
                    By.ID, 'deviceAuth_answer'
                )),
                timeout=3
            )
            return True

        return False

    def _send_secret_answer(self) -> None:
        self.driver.wait(condition=wait.element_to_be_clickable((
            By.ID, 'control_save'
        )))

        answer_input = self.driver.find_element_by_id('deviceAuth_answer')
        answer_input.send_keys(self._secret_answer)

        authorize_button = self.driver.find_element_by_id('control_save')
        authorize_button.click()

    def _extract_user_id(self) -> str:
        xpath = '//div[@data-test="userId"]'
        self.driver.wait(wait.presence_of_element_located((By.XPATH, xpath)))

        id_label = self.driver.find_element_by_xpath(xpath)
        return id_label.text.strip()

    def _extract_user_name(self) -> str:
        xpath = '//div[@data-test="userName"]'
        self.driver.wait(wait.presence_of_element_located((By.XPATH, xpath)))

        name_label = self.driver.find_element_by_xpath(xpath)
        return name_label.text.strip()

    def _extract_user_email(self) -> str:
        xpath = '//div[@data-test="userEmail"]'
        self.driver.wait(wait.presence_of_element_located((By.XPATH, xpath)))

        email_label = self.driver.find_element_by_xpath(xpath)
        return email_label.text.strip()

    def _extract_job_title(self) -> str:
        self.driver.wait(wait.presence_of_element_located((
            By.ID, 'fwh-sidebar-profile'
        )))

        sidebar = self.driver.find_element_by_id('fwh-sidebar-profile')

        job_title_label = sidebar.find_element(By.TAG_NAME, 'p')
        return job_title_label.text.strip()

    def extract_user_data(self) -> UserData:
        job_title = self._extract_job_title()

        self.driver.load(self._contact_info_url)

        if self._asked_for_secret_answer():
            self._send_secret_answer()

        user_id = self._extract_user_id()
        user_name = self._extract_user_name()
        user_email = self._extract_user_email()

        return UserData(user_id=user_id,
                        user_name=user_name,
                        email=user_email,
                        job_title=job_title)


class AddressDataExtractor(Actor):
    def __init__(
        self, driver: browser.Driver, tax_info_url: str = _TAX_INFO_URL
    ):
        super().__init__(driver)
        self._tax_info_url = tax_info_url

    def extract_address_data(self) -> AddressData:
        self.driver.load(self._tax_info_url)

        xpath = '//div[@class="text-body"]'
        div = self.driver.wait(wait.presence_of_element_located((By.XPATH,
                                                                 xpath)))

        address_info = {}
        address_info_list = div.text.split('\n')

        while len(address_info_list) > 0:
            if 'country' not in address_info:
                address_info['country'] = address_info_list[-1]
                del address_info_list[-1]
                continue

            if 'postal_code' not in address_info:
                address_info['postal_code'] = address_info_list[-1]
                del address_info_list[-1]
                continue

            if 'city' not in address_info:
                city, state = address_info_list[-1].split(', ')

                address_info['city'] = city
                address_info['state'] = state

                del address_info_list[-1]
                continue

            if 'line2' not in address_info:
                address_info['line2'] = address_info_list[-1]
                del address_info_list[-1]
                continue

            if 'line1' not in address_info:
                address_info['line1'] = address_info_list[-1]
                del address_info_list[-1]

        if 'line1' not in address_info:
            address_info['line1'] = address_info['line2']
            address_info['line2'] = ''

        return AddressData(**address_info)


def run(driver: browser.Driver, credentials: Credentials) -> Result:
    logger = log.get_logger()
    logger.info('starting scan')

    logger.info('logging in to the portal')
    authenticator = Authenticator(driver, credentials)
    authenticator.authenticate()

    logger.info('extracting job matches')
    job_matches_extractor = JobMatchesExtractor(driver)
    job_matches = job_matches_extractor.extract_job_matches()

    logger.info('extracting user data')
    user_data_extractor = UserDataExtractor(
        driver=driver, secret_answer=credentials.secret_answer
    )
    user_data = user_data_extractor.extract_user_data()

    logger.info('extracting address data')
    address_data_extractor = AddressDataExtractor(driver)
    address_data = address_data_extractor.extract_address_data()

    return Result(user=user_data,
                  address=address_data,
                  job_matches=job_matches)
