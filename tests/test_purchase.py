"""Проверки реального UI SauceDemo (запуск требует интернет и Chromium)."""

import pytest
from playwright.sync_api import Page, expect

from qa_pages import Store


@pytest.mark.e2e
def test_purchase_backpack_e2e(page: Page) -> None:
    """Основной сценарий компании: вход → покупка → успешное подтверждение."""
    store = Store(page)
    store.open_login()
    store.login()
    store.assert_catalog_open()
    store.add_backpack()
    store.open_cart()
    store.open_checkout()
    store.fill_customer("Test", "Student", "12345")
    store.assert_checkout_overview()
    store.finish()


@pytest.mark.e2e
def test_login_rejects_wrong_password(page: Page) -> None:
    """Неверный пароль должен дать понятную ошибку, не пуская в каталог."""
    store = Store(page)
    store.open_login()
    store.login(password="definitely_invalid_password")
    expect(page.locator('[data-test="error"]')).to_contain_text(
        "Username and password do not match"
    )
    expect(page.locator('[data-test="login-button"]')).to_be_visible()


@pytest.mark.e2e
def test_checkout_requires_first_name(page: Page) -> None:
    """Пустое обязательное поле блокирует оформление заказа."""
    store = Store(page)
    store.open_login()
    store.login()
    store.assert_catalog_open()
    store.add_backpack()
    store.open_cart()
    store.open_checkout()
    store.fill_customer("", "Student", "12345")
    expect(page.locator('[data-test="error"]')).to_contain_text(
        "First Name is required"
    )
    expect(page.locator(".title")).to_have_text("Checkout: Your Information")
