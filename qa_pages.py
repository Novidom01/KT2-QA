"""Небольшой объект шагов для E2E-сценария SauceDemo."""

import re

from playwright.sync_api import Page, expect

BASE_URL = "https://www.saucedemo.com/"
USERNAME = "standard_user"  # Публичный тестовый аккаунт SauceDemo
PASSWORD = "secret_sauce"  # Пароль опубликован в тестовом задании
ITEM_NAME = "Sauce Labs Backpack"


class Store:
    """Селекторы и действия, общие для тестов.

    Это не полноценный framework: класс оставлен небольшим ради объёма КТ2.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def open_login(self) -> None:
        """Открыть начальную страницу."""
        self.page.goto(BASE_URL, wait_until="domcontentloaded")

    def login(self, username: str = USERNAME, password: str = PASSWORD) -> None:
        """Ввести учётные данные и нажать кнопку входа."""
        self.page.locator('[data-test="username"]').fill(username)
        self.page.locator('[data-test="password"]').fill(password)
        self.page.locator('[data-test="login-button"]').click()

    def assert_catalog_open(self) -> None:
        """Убедиться, что открыт каталог после успешного входа."""
        expect(self.page.locator(".title")).to_have_text("Products")

    def add_backpack(self) -> None:
        """Добавить конкретный товар и проверить счётчик корзины."""
        self.page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        expect(self.page.locator(".shopping_cart_badge")).to_have_text("1")

    def open_cart(self) -> None:
        """Открыть корзину и подтвердить название товара."""
        self.page.locator(".shopping_cart_link").click()
        expect(self.page.locator(".cart_item .inventory_item_name")).to_have_text(ITEM_NAME)

    def open_checkout(self) -> None:
        """Перейти к оформлению заказа."""
        self.page.locator('[data-test="checkout"]').click()
        expect(self.page.locator(".title")).to_have_text("Checkout: Your Information")

    def fill_customer(self, first: str, last: str, postal: str) -> None:
        """Заполнить контактные поля и перейти к обзору заказа."""
        self.page.locator('[data-test="firstName"]').fill(first)
        self.page.locator('[data-test="lastName"]').fill(last)
        self.page.locator('[data-test="postalCode"]').fill(postal)
        self.page.locator('[data-test="continue"]').click()

    def assert_checkout_overview(self) -> None:
        """Проверить, что в обзоре заказа остался выбранный товар."""
        expect(self.page.locator(".title")).to_have_text("Checkout: Overview")
        expect(self.page.locator(".cart_item .inventory_item_name")).to_have_text(ITEM_NAME)
        total_label = self.page.locator(".summary_total_label").inner_text()
        total = re.fullmatch(r"Total: \$(\d+\.\d{2})", total_label.strip())
        assert total is not None and float(total.group(1)) > 0, (
            f"Некорректная итоговая сумма заказа: {total_label!r}"
        )

    def finish(self) -> None:
        """Завершить заказ и проверить подтверждение со стороны сайта."""
        self.page.locator('[data-test="finish"]').click()
        expect(self.page.locator(".title")).to_have_text("Checkout: Complete!")
        expect(self.page.locator('[data-test="complete-header"]')).to_have_text(
            "Thank you for your order!"
        )
