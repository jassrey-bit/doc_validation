from pages.login_page import LoginPage

def test_login(page):

    login = LoginPage(page)

    login.navigate()

    login.login(
        "standard_user",
        "secret_sauce"
    )

    assert "inventory" in page.url