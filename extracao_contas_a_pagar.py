import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import re
import os

# Data atual
data = time.strftime("%d/%m/%Y")
data_ano = time.strftime("%Y")
data_mes = time.strftime("%m")

# Conversão de meses para extenso
meses_por_extenso = {
    "01": "1 - JANEIRO",
    "02": "2 - FEVEREIRO",
    "03": "3 - MARÇO",
    "04": "4 - ABRIL",
    "05": "5 - MAIO",
    "06": "6 - JUNHO",
    "07": "7 - JULHO",
    "08": "8 - AGOSTO",
    "09": "9 - SETEMBRO",
    "10": "10 - OUTUBRO",
    "11": "11 - NOVEMBRO",
    "12": "12 - DEZEMBRO"
}
data_mes = meses_por_extenso.get(data_mes, data_mes)
data_str = str(data)

# Caminhos do ChromeDriver e do Chrome
chrome_driver_path = r"C/documents"
chrome_options_binary_location = r"c\documents"

# Opções do Chrome
chrome_options = Options()
chrome_options.binary_location = chrome_options_binary_location

download_dir = 'C://projects//Request_marketing//dist'
chrome_prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("prefs", chrome_prefs)

# Inicializando o WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Aguardando a página carregar
wait = WebDriverWait(driver, 20)
time.sleep(1)

# Classe para extrair as notas a pagar do site do BB
class ExtracaoBBNotasAPagar:
    def __init__(self, driver, download_dir):
        self.driver = driver
        self.download_dir = download_dir

    def execute(self):
        self.extraindo_contas_a_pagar(data_str)

    def pegar_arquivos_em_diretorios(self):
        return set(os.listdir(self.download_dir))

    def esperar_download_concluir(self, timeout=30):
        arquivos_antes = self.pegar_arquivos_em_diretorios()
        tempo_fim = time.time() + timeout

        while time.time() < tempo_fim:
            arquivos_depois = self.pegar_arquivos_em_diretorios()
            novo_arquivo = arquivos_depois - arquivos_antes
            if novo_arquivo:
                return novo_arquivo.pop()
            time.sleep(1)
        return None

    def extraindo_contas_a_pagar(self, data_str):
        lista_credenciais = [
            '/html/body/app/div[1]/login/div/form/input[1]',
            '/html/body/app/div[1]/login/div/form/input[2]'
        ]
        for index, credenciais in enumerate(lista_credenciais):
            campos = wait.until(EC.presence_of_element_located((By.XPATH, credenciais)))
            campos.click()
            time.sleep(1)
            campos.clear()
            time.sleep(1)
            if index == 0:
                user = ''
                campos.send_keys(user)
            else:
                password = ''
                campos.send_keys(password)
        botao_login = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app/div[1]/login/div/form/button')))
        botao_login.click()
        time.sleep(2)
        botao_download = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app/div[1]/home/div/div/div[2]/div/div[1]')))
        botao_download.click()
        time.sleep(2)
        ordenar_extrato = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app/div[1]/download/div/table/thead/tr/th[3]/button/i')))
        ordenar_extrato.click()
        ordenar_extrato.click()

        tbody = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app/div[1]/download/div/table/tbody')))
        linhas = tbody.find_elements(By.XPATH, './tr')

        numeros_procurados = ['841505071', '841308803']
        contador_downloads = 0
        for numero_procurado in numeros_procurados:
            contador = 0
            for linha in linhas:
                contador += 1
                numero = linha.find_element(By.XPATH, './/td[@class="col-md-2 text-left"]').text
                data = linha.find_element(By.XPATH, './/td[@class="col-md-1 text-center"]').text
                texto_data = data
                match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_data)
                if match_data:
                    texto_data = match_data.group(1)
                texto_numero = numero
                match_numero = re.search(r'Contrato (\d+) -', texto_numero)
                if match_numero:
                    texto_numero = match_numero.group(1)
                if numero_procurado == texto_numero and texto_data == data_str:
                    botao_download = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/app/div[1]/download/div/table/tbody/tr[{contador}]/td[7]/button/i')))
                    driver.execute_script("arguments[0].scrollIntoView();", botao_download)
                    actions = ActionChains(driver)
                    actions.move_to_element(botao_download).click().perform()
                    time.sleep(20)
                    driver.execute_script("arguments[0].click();", botao_download)
                    arquivo_nome = self.esperar_download_concluir()
                    if arquivo_nome is not None:
                        print(f'Arquivo baixado: {arquivo_nome}')
                    else:
                        print('Erro ao baixar o arquivo')
                    contador_downloads += 1
                    print(f'Quantidade de downloads: {contador_downloads}')
                    break

# Execução do script
if __name__ == '__main__':
    extracao = ExtracaoBBNotasAPagar(driver, download_dir)
    extracao.execute()
