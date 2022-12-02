from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Bot():
    def __init__(self, login, password) -> None:
        self.__base_url = 'https://ok.ru/'
        self.__login = login
        self.__password = password
        self.error = ''

        (self.driver, self.wait) = self.create_driver()
        self.is_auth = self.auth()

    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=800,600")

        driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
        wait = WebDriverWait(driver, 2)
        return driver, wait

    def auth(self):
        """
        Метод авторизации
        """
        self.driver.get(self.__base_url)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[name="st.email"]'))).send_keys(self.__login)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input[name="st.password"]'))).send_keys(self.__password)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'input.button-pro'))).click()
        try:
            if len(self.driver.find_element(By.CSS_SELECTOR, '.input-e').text) > 0:
                self.error = self.driver.find_element(By.CSS_SELECTOR, '.input-e').text
                return False
        except Exception as _:
            pass

        return True


    def __scroll(self):
        """
        Метод для прокрутки страницы
        """
        i = 0
        while i < 5:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
            self.driver.execute_script("window.scrollTo(0, 0);")
            sleep(1)
            i += 1


    def create_post(self, comment):
        """
        Метод создания поста
        """
        self.driver.get(self.__base_url + 'post')
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.posting_itx'))).send_keys(comment)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, '.posting_submit'))).click()
        self.driver.get(self.__base_url)


    def create_comment_in_user_profile(self, ids, comment):
        """
        Метод создания комментария подсты пользователя
        """
        ids = [ids]

        for _id in ids:
            self.driver.get(self.__base_url + f'profile/{_id}')
            self.__scroll()

            elements1 = self.driver.find_elements(
                By.CSS_SELECTOR,
                'div.feed-w > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1) > div:nth-child(1) > a:nth-child(1)'
            )
            elements2 = self.driver.find_elements(
                By.CSS_SELECTOR, 'div.feed_f > ul:nth-child(1) > li:nth-child(1) > div:nth-child(1) > a:nth-child(1)'
            )

            elements = [*elements1, *elements2]

            urls = [element.get_attribute('href') for element in elements]
            print(urls)
            for url in urls:
                self.driver.get(url)

                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, '.gwt-inputButton').click()
                except Exception as _:
                    pass

                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '#ok-e-d'))).send_keys(comment)

                self.wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, '#ok-e-d_button'))).click()


    def like_users(self, ids: int | list):
        """
        Метод лайка пользователей
        """
        if isinstance(ids, int):
            ids = [ids]

        for id in ids:
            self.driver.get(self.__base_url + f'profile/{str(id)}')
            self.__scroll()

            like_button = self.driver.find_elements(By.XPATH, '//span[text()="Класс"]')

            for like in like_button:
                like.click()
