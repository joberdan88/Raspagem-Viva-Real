import re
import time
import os
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Inicializamos as listas para guardar as informações
link_imovel = []
address = []
neighbor = []
anunciante = []
area = []
tipo = []
room = []
bath = []
park = []
price = []

# Definimos o número de páginas que queremos coletar
pages_number = 8

# Inicializa o tempo de execução
tic = time.time()

# Função para iniciar o driver do Chrome
def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar em modo headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f"user-agent={random_user_agent()}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Função para gerar um User-Agent randômico
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    ]
    return random.choice(user_agents)

# Função para coletar dados de cada página
def coletar_dados(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'property-card__content')))
    except TimeoutException:
        print(f"Timeout ao carregar a página: {url}")
        return
    except NoSuchWindowException:
        raise NoSuchWindowException("A janela do navegador foi fechada.")
    except WebDriverException as e:
        print(f"Erro no WebDriver: {e}")
        return
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    imoveis = soup.find_all('div', class_='property-card__content')

    for imovel in imoveis:
        try:
            link = imovel.find('a', class_='property-card__content-link')['href']
            link_imovel.append(link)
        except:
            link_imovel.append(None)
        
        try:
            end = imovel.find('span', class_='property-card__address').get_text(strip=True)
            address.append(end)
        except:
            address.append(None)
        
        try:
            neigh = imovel.find('span', class_='property-card__address').get_text(strip=True)
            neighbor.append(neigh)
        except:
            neighbor.append(None)
        
        try:
            anunc = imovel.find('span', class_='property-card__deal-type').get_text(strip=True)
            anunciante.append(anunc)
        except:
            anunciante.append(None)
        
        try:
            area_info = imovel.find('li', class_='property-card__detail-area').get_text(strip=True)
            area.append(area_info)
        except:
            area.append(None)
        
        tipo_info = "Apartamento"
        tipo.append(tipo_info)
        
        try:
            quartos_info = imovel.find('li', class_='property-card__detail-room').get_text(strip=True)
            room.append(quartos_info)
        except:
            room.append(None)
        
        try:
            banheiros_info = imovel.find('li', class_='property-card__detail-bathroom').get_text(strip=True)
            bath.append(banheiros_info)
        except:
            bath.append(None)
        
        try:
            vagas_info = imovel.find('li', class_='property-card__detail-garage').get_text(strip=True)
            park.append(vagas_info)
        except:
            park.append(None)
        
        try:
            preco_info = imovel.find('div', class_='property-card__price').get_text(strip=True)
            price.append(preco_info)
        except:
            price.append(None)

# Inicia o driver do Chrome
driver = iniciar_driver()

# Coletar dados das páginas especificadas
base_url = "https://www.vivareal.com.br/aluguel/rj/rio-de-janeiro/zona-sul/botafogo/apartamento_residencial/?pagina="
for page in range(1, pages_number + 1):
    url = base_url + str(page)
    try:
        coletar_dados(driver, url)
        time.sleep(random.uniform(5, 10))  # Atraso randômico entre 5 e 10 segundos
    except NoSuchWindowException:
        print("Janela do navegador fechada inesperadamente. Reiniciando o driver.")
        driver = iniciar_driver()
        coletar_dados(driver, url)
    except WebDriverException as e:
        print(f"Erro no WebDriver: {e}. Reiniciando o driver.")
        driver.quit()
        driver = iniciar_driver()
        coletar_dados(driver, url)

# Fechar o navegador
driver.quit()

# Salvar os dados em um arquivo CSV
data = {
    'Link': link_imovel,
    'Endereço': address,
    'Bairro': neighbor,
    'Anunciante': anunciante,
    'Área': area,
    'Tipo': tipo,
    'Quartos': room,
    'Banheiros': bath,
    'Vagas': park,
    'Preço': price
}

df = pd.DataFrame(data)
df.to_csv('imoveis_botafogo.csv', index=False)

# Imprimir o diretório atual
print("Arquivo foi salvo no diretório:", os.getcwd())
toc = time.time()
print("Tempo de execução:", toc - tic, "segundos")
