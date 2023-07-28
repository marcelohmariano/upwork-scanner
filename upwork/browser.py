from typing import Any

import urllib3.exceptions
from retry import retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

wait = expected_conditions


@retry(urllib3.exceptions.ProtocolError, tries=5, delay=2)
def _create_remote_driver(
    url: str, options: webdriver.ChromeOptions
) -> webdriver.Remote:
    return webdriver.Remote(command_executor=url, options=options)


class Driver:
    def __init__(self, selenium_server_url: str, selenium_wait_timeout: float):
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')

        self._driver = _create_remote_driver(selenium_server_url, options)
        self._wait_timeout = selenium_wait_timeout

    def __enter__(self) -> 'Driver':
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self._driver.quit()

    def load(self, url: str) -> None:
        self._driver.get(url)

    def quit(self) -> None:
        self._driver.quit()

    def wait(self, condition: Any, timeout: float = 60.0) -> WebElement:
        timeout = timeout or self._wait_timeout
        return WebDriverWait(self._driver, timeout).until(condition)

    def execute_script(self, script: str, *args) -> Any:
        return self._driver.execute_script(script, *args)

    def find_element_by_id(self, value: str) -> WebElement:
        return self._driver.find_element(By.ID, value)

    def find_elements_by_css(self, value: str) -> list[WebElement]:
        return self._driver.find_elements(By.CSS_SELECTOR, value)

    def find_element_by_xpath(self, value: str) -> WebElement:
        return self._driver.find_element(By.XPATH, value)

    def set_input_text(self, id_: str, text: str) -> None:
        self.wait(wait.visibility_of_element_located((By.ID, id_)))
        element = self.find_element_by_id(id_)
        element.send_keys(text)

    def click_button(self, id_: str) -> None:
        self.wait(wait.element_to_be_clickable((By.ID, id_)))
        element = self.find_element_by_id(id_)
        element.click()

    @property
    def url(self) -> str:
        return self._driver.current_url
