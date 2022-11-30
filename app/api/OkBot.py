
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        chrome_options.add_argument("--window-size=1366,768")
        
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

    
        return self.driver.get_screenshot_as_png()

    def create_comment_in_user_profile(self, ids, comment):
        """
        Метод создания комментария подсты пользователя
        """
        ids = [ids]

        # imgs_bytes = []
        
        for _id in ids:
            self.driver.get(self.__base_url + f'profile/{_id}')
            self.__scroll()

            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                'div.feed-w > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > ul:nth-child(2) > li:nth-child(1) > div:nth-child(1) > a:nth-child(1)'
                )
            urls = [element.get_attribute('href') for element in elements]

            for url in urls:
                self.driver.get(url)
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 
                                            '.gwt-inputButton').click()
                except Exception as _:
                    pass
                
                # self.driver.find_element(By.XPATH, '//*[@id="ok-e-d"]').send_keys(comment)
                # self.driver.find_element(By.CSS_SELECTOR, '#ok-e-d').send_keys(Keys.RETURN)

                # imgs_bytes.append(self.driver.get_screenshot_as_png())
        # return imgs_bytes


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
            
            # like_button = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[class="widget_cnt controls-list_lk js-klass js-klass-action h-mod"]')))
            for like in like_button:
                like.click()