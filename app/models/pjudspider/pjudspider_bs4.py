import random
import time
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

class pjudspider:
    results = []
    service = Service("path/to/chromedriver")

    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.driver = None
        self.ritcompetencia = "3"
        self.corte = "90"
        self.tribunal = "274"
        self.ritlibro = "C"
        self.ritnumero = "2479"
        self.ritanio =  "2022"
    
    def random_delay(self):
        delay = random.uniform(1, 3)
        time.sleep(delay)
    
    def move_mouse(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self.random_delay()
    
    def parse(self):
        chrome_options = Options()
        service = Service(self.chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://oficinajudicialvirtual.pjud.cl/home/"
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        function_name = "accesoConsultaCausas"
        if function_name == "accesoConsultaCausas":
            button = self.driver.find_element(By.XPATH, "//div[@class='row']/div[@class='col-sm-4']/div[@class='dropdown']/button[contains(text(), 'Consulta causas')]")

            #Esto ayuda a que no detecten el bot
            self.move_mouse(button)
            self.random_delay()
            button.click()
            time.sleep(5)
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            script_code_C = '''
            var form = document.getElementById('formConsulta');
            form.competencia.value = "{}";
            form.competencia.dispatchEvent(new Event('change', {{ bubbles: true }}));
            setTimeout(function() {{
                form.conCorte.value = "{}";
                form.conCorte.dispatchEvent(new Event('change', {{ bubbles: true }}));
                setTimeout(function() {{
                    form.conTribunal.value = "{}";
                    form.conTipoCausa.value = "{}";
                    form.conRolCausa.value = "{}";
                    form.conEraCausa.value = "{}";
                    var submitButton = document.querySelector('button[type="submit"]');
                    submitButton.click();
                }}, 1000);
            }}, 1000);
            '''.format(self.ritcompetencia, self.corte, self.tribunal, self.ritlibro, self.ritnumero, self.ritanio)
            self.driver.execute_script(script_code_C)

            time.sleep(5)
            search_button = self.driver.find_element(By.XPATH, "//a[@class='toggle-modal']")
            search_button.click()
            time.sleep(5)
            self.parse_results(soup)

    def parse_results(self, soup):
        modal_div1 = self.driver.find_element(By.XPATH, '//div[@id="modalDetalleCivil"]')
        tables1 = modal_div1.find_elements(By.XPATH, './/table[@class="table table-responsive table-titulos"]')
        content1 = modal_div1.find_elements(By.XPATH, './/table[@class="table table-bordered table-striped table-hover"]')
        litigantes_tab1 = modal_div1.find_element(By.XPATH, '//a[text()="Litigantes"]')

        for i in range(1):
            table = tables1[i]
            table_rows = table.find_elements(By.TAG_NAME, "tr")
            for row in table_rows:
                row_data = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                print(row_data)

        if len(tables1) >= 2:
            table = tables1[1]
            table_rows = table.find_elements(By.TAG_NAME, "tr")
            for index, row in enumerate(table_rows, start=1):
                row_data = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
                td_elements = row.find_elements(By.TAG_NAME, "td")
                if len(td_elements) >= 3:
                    """pdf_link1 = td_elements[0].find_element(By.XPATH, './/a')
                    pdf_link1.click()
                    self.download_pdf("t_demanda")

                    pdf_folder1 = td_elements[1].find_element(By.XPATH, './/a')
                    pdf_folder1.click()
                    time.sleep(4)
                    self.scan_folder("modalAnexoCausaCivil", "anexo_causa")

                    pdf_link2 = td_elements[2].find_element(By.XPATH, './/a')
                    pdf_link2.click()
                    self.download_pdf("c_envio")"""
                    self.scan_tables(content1, litigantes_tab1)

    def download_pdf(self, index):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(5)
        pdf_url = self.driver.current_url
        rol = self.ritlibro + "-" + self.ritnumero + "-" + self.ritanio
        folder_name = rol
        file_name = f"{index}.pdf"
        folder_path = f"pdf/{folder_name}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99 Safari/537.36"}
        response = requests.get(pdf_url, headers=headers)
        with open(os.path.join(folder_path, file_name), "wb") as file:
            file.write(response.content)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def scan_tables(self, content, litigantes_tab):
        if len(content) > 0:
            table_header_rows = content[0].find_elements(By.TAG_NAME, "th")
            header_data = [th.text.strip() for th in table_header_rows]
        for index, element in enumerate(content):
            table_rows = element.find_elements(By.TAG_NAME, "tr")
            for row in table_rows:
                table_cells = row.find_elements(By.TAG_NAME, "td")
                if len(table_cells) > 4:
                    row_data = {}
                    for j in range(len(table_cells)):
                        cell_text = table_cells[j].text.strip()
                        header = header_data[j] if j < len(header_data) else f"td{j+1}"
                        row_data[header] = cell_text
                    print(row_data)
                    try:
                        pdf_form = table_cells[1].find_element(By.TAG_NAME, 'form')
                        pdf_links = pdf_form.find_elements(By.TAG_NAME, 'a')
                        folio_number = row_data.get("Folio", "")
                        if len(pdf_links) >= 1:
                            pdf_link_1 = pdf_links[0]
                            pdf_link_1.click()
                            self.download_pdf(f"f_{folio_number}")
                            if len(pdf_links) >= 2:
                                pdf_link_2 = pdf_links[1]
                                pdf_link_2.click()
                                self.download_pdf(f"ec_{folio_number}")
                                time.sleep(5)
                        else:
                            print("No PDF links found in the table cell.")
                    except NoSuchElementException:
                        print("No PDF link found in the table cell.")
                    self.random_delay()
                    try:
                        pdf_folder = table_cells[2].find_element(By.TAG_NAME, 'a')
                        folio_number = row_data.get("Folio", "")
                        pdf_folder.click()
                        time.sleep(4)
                        self.scan_folder("modalAnexoSolicitudCivil", f"f_{folio_number}")
                    except NoSuchElementException:
                        print("No folder found.")
                        
        litigantes_tab.click()
        self.random_delay()
        for element in content:
            table_headers = element.find_elements(By.TAG_NAME, "th")
            if len(content) > 0:
                header_data = [th.text.strip() for th in table_headers]
            table_rows = element.find_elements(By.TAG_NAME, "tr")
            for row in table_rows:   
                table_cells = row.find_elements(By.TAG_NAME, "td")
                if len(table_cells) == 4:
                    row_data = {}
                    for j in range(len(table_cells)):
                        cell_text = table_cells[j].text.strip()
                        header = header_data[j] if j < len(header_data) else f"td{j+1}"
                        row_data[header] = cell_text
                    print(row_data)

    def scan_folder(self, modal_id, name):
        modal_div2 = self.driver.find_element(By.XPATH, f'//div[@id="{modal_id}"]')
        tables2 = modal_div2.find_elements(By.XPATH, './/table[@class="table table-responsive table-titulos"]')
        content2 = modal_div2.find_elements(By.XPATH, './/table[@class="table table-bordered table-striped table-hover"]')

        if len(content2) > 0:
            table_header_rows = content2[0].find_elements(By.TAG_NAME, "th")
            header_data = [th.text.strip() for th in table_header_rows]

        for index, element in enumerate(content2):
            table_rows = element.find_elements(By.TAG_NAME, "tr")
            link_found = False  # Flag to track if a link was found

            for row in table_rows:
                try:
                    # Re-fetch the table cells to handle StaleElementReferenceException
                    table_cells = row.find_elements(By.TAG_NAME, "td")
                except StaleElementReferenceException:
                    # Re-fetch the table cells if the element is stale
                    table_cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(table_cells) == 3:
                    row_data = {}
                    for j in range(len(table_cells)):
                        cell_text = table_cells[j].text.strip()
                        header = header_data[j] if j < len(header_data) else f"td{j+1}"
                        row_data[header] = cell_text
                    print(row_data)

                    try:
                        pdf_form = table_cells[0].find_element(By.TAG_NAME, 'form')
                        pdf_links = pdf_form.find_elements(By.TAG_NAME, 'a')
                        Referencia = row_data.get("Referencia", "")
                        if len(pdf_links) >= 1:
                            pdf_link_1 = pdf_links[0]
                            pdf_link_1.click()
                            self.download_pdf(f"{name}_{Referencia}")
                            time.sleep(5)

                    except NoSuchElementException:
                        pass
        time.sleep(3)
        close_button = modal_div2.find_elements(By.CLASS_NAME, 'close')[0]
        close_button.click()
        return

automation = pjudspider("path_to_chromedriver")
automation.parse()