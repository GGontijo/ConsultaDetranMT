from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from helpers.config_helper import Config
from interfaces.selenium_interface import SeleniumInterface


class SeconService(SeleniumInterface):

    def __init__(self) -> None:
        _config = Config()
        self.config = _config.get_config("SeleniumDriver")
        self.driver_path = self.config["driver_path"]

    def run(self) -> str:
        if not self.ready:
            return None

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(self.driver_path, options=self.options)
        self.driver.get(self.url)
        self.driver.implicitly_wait(5)
        submit_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.wait_element)))
        placa_field = self.driver.find_element(by= By.ID, value=self.placa_field_id)
        renavam_field = self.driver.find_element(by= By.ID, value=self.renavam_field_id)
        placa_field.send_keys(self.placa)
        renavam_field.send_keys(self.renavam)
        submit_button.click()
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.wait_ready_page_element)))
        if len(self.driver.window_handles) > 0:
            self.driver.switch_to.window(self.driver.window_handles[1])
            
        self.page_html = self.driver.page_source
        self.driver.quit()


    def prepare(self, parameters : dict) -> str:
        self.ready = False
        try:
            if parameters["placa"] or parameters["renavam"]:
                self.placa = parameters["placa"]
                self.renavam = parameters["renavam"]
        except Exception as e:
            return f'Parametros insuficiente: {e}'
        

        self.url = self.config("secon")
        self.placa_field_id = self.config["secon_placa_field_id"]
        self.renavam_field_id = self.config["secon_renavam_field_id"]
        self.wait_element = self.config["secon_presence"]
        self.wait_ready_page_element = self.config["secon_ready_page_element"]
                

        self.ready = True
        return 'Parametros carregados com sucesso!'
