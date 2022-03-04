import time

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


@pytest.mark.selenium
def test_dashboard_admin_login(
    live_server,
    create_admin_user,
    # db_fixture_setup,
    chrome_browser_instance,
):

    browser = chrome_browser_instance

    browser.get(("%s%s" % (live_server.url, "/admin/login/")))

    email = browser.find_element(By.NAME, "username")
    user_password = browser.find_element(By.NAME, "password")
    submit = browser.find_element(By.XPATH, '//input[@value="Log in"]')

    email.send_keys("admin@example.com")
    user_password.send_keys("password")
    submit.send_keys(Keys.RETURN)
    # time.sleep(100)
    assert "Site administration" in browser.page_source
