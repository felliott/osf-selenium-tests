import settings

from api import osf_api
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from components.navbars import EmberNavbar
from pages.base import OSFBasePage, GuidBasePage
from base.locators import Locator, ComponentLocator, GroupLocator


class BaseQuickfilesPage(OSFBasePage):

    navbar = ComponentLocator(EmberNavbar)

    # def verify(self):
    #     """Verify that you are on the expected page by confirming the page's `identity`
    #     element is present on the page.
    #     """

    #     try:
    #         WebDriverWait(self.driver, settings.VERY_LONG_TIMEOUT).until(
    #             page_is_prerendered()
    #         )
    #     except(TimeoutException, StaleElementReferenceException):
    #         raise ValueError('Embosed page never finished loading') from None

    #     return super().verify()


class page_is_prerendered(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
    def __init__(self):
        pass

    def __call__(self, driver):
        # return True
        return driver.execute_script('return window.prerenderReady;')


class QuickfilesPage(BaseQuickfilesPage, GuidBasePage):
    """Main page for a user's quickfiles. Take's a user's guid, but defaults to USER_ONE's if a guid isn't given.
    """
    base_url = settings.OSF_HOME + '/{guid}/quickfiles/'
    user = osf_api.current_user()

    def __init__(self, driver, verify=False, guid=user.id):
        super().__init__(driver, verify, guid)

    # TODO: Add download buttons back in when you have a way to distingish them
    identity = Locator(By.CSS_SELECTOR, '#quickfiles-dropzone')
    loading_indicator = Locator(By.CSS_SELECTOR, '.ball-scale')
    upload_button = Locator(By.CSS_SELECTOR, '.dz-upload-button')
    share_button = Locator(By.CSS_SELECTOR, '.btn .fa-share-alt')
    view_button = Locator(By.CSS_SELECTOR, '.btn .fa-file-o')
    help_button = Locator(By.CSS_SELECTOR, '.btn .fa-info')
    filter_button = Locator(By.CSS_SELECTOR, '.btn .fa-search')
    rename_button = Locator(By.CSS_SELECTOR, '.btn .fa-pencil')
    delete_button = Locator(By.CSS_SELECTOR, '.btn .fa-trash')
    move_button = Locator(By.CSS_SELECTOR, '.btn .fa-level-up')

    # Group Locators
    files = GroupLocator(By.CSS_SELECTOR, '._file-browser-item_1v8xgw')
    file_titles = GroupLocator(By.CSS_SELECTOR, '._file-browser-item_1v8xgw a')


class QuickfileDetailPage(BaseQuickfilesPage, GuidBasePage):
    identity = Locator(By.CSS_SELECTOR, '._TitleBar_1628nl')
