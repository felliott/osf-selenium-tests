import settings

import urllib.parse
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException

from components.navbars import HomeNavbar
from base.locators import BaseElement, ComponentLocator
from base.exceptions import HttpError, PageException


class BasePage(BaseElement):
    url = None

    def __init__(self, driver, verify=False):
        super().__init__(driver)

        if verify:
            self.check_page()

    def goto(self, expect_redirect_to=None):
        """Navigate to a page based on its `url` attribute
        and confirms you are on the expected page.

        If you are not actually expecting to end up on the page you attempt to `goto`
        (for example when testing permissions) you can set `expect_redirect_to` equal to
        any BasePage class and it will be verified you wind up on that page instead.
        """

        self.driver.get(self.url)

        if expect_redirect_to:
            if self.url not in self.driver.current_url:
                raise PageException('Unexpected url structure: `{}`'.format(self.driver.current_url))
            expect_redirect_to(self.driver, verify=True)
        else:
            self.check_page()

    def check_page(self):
        if not self.verify():
            # handle any specific kind of error before go to page exception
            self.error_handling()
            raise PageException('Unexpected page structure: `{}`'.format(self.driver.current_url))

    def verify(self):
        """Verify that you are on the expected page by confirming the page's `identity`
        element is present on the page.
        """
        return self.identity.present()

    def error_handling(self):
        pass

    def reload(self):
        self.driver.refresh()

    def scroll_into_view(self, element):
        self.driver.execute_script('arguments[0].scrollIntoView(false);', element)
        # Account for navbar
        self.driver.execute_script('window.scrollBy(0, 55)')

    def drag_and_drop(self, source_element, dest_element):
        source_element.click()
        ActionChains(self.driver).drag_and_drop(source_element, dest_element).perform()
        # Note: If you close the browser too quickly, the drag/drop may not go through
        sleep(1)


class OSFBasePage(BasePage):
    """
    Note: All pages must have a unique identity or overwrite `verify`
    """
    url = settings.OSF_HOME
    navbar = ComponentLocator(HomeNavbar)

    def __init__(self, driver, verify=False):
        super().__init__(driver, verify)

    @property
    def error_heading(self):
        try:
            error_head = self.driver.find_element(By.CSS_SELECTOR, 'h2#error')
        except NoSuchElementException:
            return None
        else:
            return error_head.text

    def error_handling(self):
        # If we've got an error message here from osf, grab it
        if self.error_heading:
            raise HttpError(self.error_heading.get_attribute('data-http-status-code'))

    def is_logged_in(self):
        return self.navbar.is_logged_in()

    def is_logged_out(self):
        return self.navbar.is_logged_out()


class GuidBasePage(OSFBasePage):
    base_url = urllib.parse.urljoin(settings.OSF_HOME, '{guid}')
    guid = ''

    def __init__(self, driver, verify=False, guid='', domain=settings.OSF_HOME):
        super().__init__(driver, verify)
        # self.domain = domain
        self.guid = guid

    @property
    def url(self):
        if '{guid}' in self.base_url:
            return self.base_url.format(guid=self.guid)
        else:
            raise ValueError('No space in base_url for GUID specified.')


class EmbOSFBasePage(OSFBasePage):
    """
    EmbOSF-ed pages set ``document.prerenderReady`` equals to 
    """

    # def __init__(self, driver, verify=False, *args):
    def __init__(self, driver, verify=False):
        super().__init__(driver, verify)

    def verify(self):
        """Verify that you are on the expected page by confirming the page's `identity`
        element is present on the page.
        """

        try:
            WebDriverWait(self.driver, settings.VERY_LONG_TIMEOUT).until(
                page_is_prerendered()
            )
        except(TimeoutException, StaleElementReferenceException):
            raise ValueError('Embosed page never finished loading') from None

        return super().verify()

    # def _prerender_is_ready(self):
    #     return self.driver.execute_script('return window.prerenderReady;') == 'complete'


class page_is_prerendered(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self):
        pass

    def __call__(self, driver):
        # return True
        return driver.execute_script('return window.prerenderReady;') == 'complete'
