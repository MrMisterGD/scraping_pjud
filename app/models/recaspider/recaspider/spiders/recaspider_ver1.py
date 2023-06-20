import scrapy
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scrapy.http import FormRequest
import logging
from app.models.reca import Reca
from app.models.persona import Persona
logging.getLogger('selenium').setLevel(logging.WARNING)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class Recaspider(scrapy.Spider):

    name = "recaspider_ver1"
    cursor = None
    results = []
    allowed_domains = ["reca.pjud.cl"]
    start_urls = ["https://reca.pjud.cl/NRECA/MenuForwardAction.do?method=cargaBusquedaPorRut"]

    #Es basicamente lo que permite usar la consola del navegador con los comandos en JS
    def __init__(self, rut=None, dv=None, *args, **kwargs):
        super(Recaspider, self).__init__(*args, **kwargs)
        self.rut = rut
        self.dv = dv
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 5)
        screen_width = 1920
        screen_height = 1080
        self.driver.set_window_size(screen_width, screen_height)
        print("Spider initialized")
        print("Spider __init__ for rut and dv:", rut + "-" + dv)
        
    def parse(self, response):
        rut = self.rut
        dv = self.dv
        print("Parse method called for rut and dv:", rut + "-" + dv)

        script_code_C = '''
            document.BuscaCausasForm.action = "busquedaCausas.do?method=findByRut";
            document.BuscaCausasForm.RUT_Rut.value = "{}";
            document.BuscaCausasForm.RUT_Rut_Db.value = "{}";
            document.BuscaCausasForm.RUT_Cod_Competencia.value = "C";
            document.BuscaCausasForm.submit();
        '''.format(rut, dv)

        script_code_L = '''
            document.BuscaCausasForm.action = "busquedaCausas.do?method=findByRut";
            document.BuscaCausasForm.RUT_Rut.value = "{}";
            document.BuscaCausasForm.RUT_Rut_Db.value = "{}";
            document.BuscaCausasForm.RUT_Cod_Competencia.value = "L";
            document.BuscaCausasForm.submit();
        '''.format(rut, dv)

        self.driver.get(response.url)

        # Busqueda Civil
        self.driver.execute_script(script_code_C)
        try:
            wait = WebDriverWait(self.driver, 2)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'filadostabla')))
            updated_response_civil = scrapy.http.HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8'
            )
            self.parse_results(updated_response_civil, rut, dv)
        except TimeoutException:
            print("Table with class 'filadostabla' not found for Busqueda Civil.")

        # Busqueda Laboral
        self.driver.execute_script(script_code_L)
        try:
            wait = WebDriverWait(self.driver, 2)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'filadostabla')))
            updated_response_laboral = scrapy.http.HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8'
            )
            self.parse_results(updated_response_laboral, rut, dv)
        except TimeoutException:
            print("Table with class 'filadostabla' not found for Busqueda Laboral.")

    def parse_results(self, response, rut, dv):
        Persona.save_persona(rut, dv)
        persona_id = Persona.get_persona_id(rut, dv)
        page_number = 2
        while page_number < 100:
            try:
                thead_content = response.xpath('//table//thead//th[position() > 1]//text()').getall()
                thead_content = [text.strip() for text in thead_content if text.strip()]
                tbody_rows = response.xpath('//table//tbody//tr')

                if not tbody_rows:
                    print("Table body rows not found")
                else:
                    print("Number of table body rows: %d" % len(tbody_rows))

                for row in tbody_rows:
                    row_values = row.xpath('.//td[position() > 1]//text()').getall()
                    row_values = [text.strip() for text in row_values if text.strip()]
                    row_data = dict(zip(thead_content, row_values))

                    #Reca.save_Reca(persona_id, row_data)
                    Recaspider.results.append(row_data)
                    
                tbody_content = [row.get() for row in tbody_rows]

                try:
                    next_page_link = self.driver.find_element(By.XPATH, f'.//span[@id="li{page_number}"]/a[@id="len{page_number}"]')

                    self.driver.execute_script("arguments[0].scrollIntoView();", next_page_link)
                    next_page_link.click()
                    try:
                        self.wait.until(EC.staleness_of(self.driver.find_element(By.XPATH, '//table')))
                    except TimeoutException:
                        print("Table on the next page not found")

                    response = scrapy.http.HtmlResponse(
                    url=self.driver.current_url,
                    body=self.driver.page_source,
                    encoding='utf-8'
                    )

                except NoSuchElementException:
                    break
                page_number += 1
            except NoSuchElementException:
                break
        print("RESULTADOS:", Recaspider.results)

def update_settings(settings):
    settings.set("CONCURRENT_REQUESTS", 32)
    settings.set("DOWNLOAD_DELAY", 2)