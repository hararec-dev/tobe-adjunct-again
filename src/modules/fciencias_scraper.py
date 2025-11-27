import logging
import os
import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from decouple import config
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class FcienciasScraper:
    def __init__(self, headless=True):
        self.base_url = config("FCIENCIAS_BASE_URL")
        self.username = config("FCIENCIAS_USERNAME")
        self.password = config("FCIENCIAS_PASSWORD")
        self.wait_timeout = config("WAIT_TIMEOUT", default=15, cast=int)
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura el WebDriver para Selenium"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, self.wait_timeout)

    def login(self):
        """Realiza el login en el portal de la facultad"""
        try:
            logger.info("Iniciando sesión en el portal...")
            self.driver.get(f"{self.base_url}/acceder")

            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)

            # Enviar formulario
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Acceder')]")
            login_button.click()

            # Esperar a que se complete el login (verificando que estamos en una página diferente)
            self.wait.until(EC.url_changes(f"{self.base_url}/acceder"))
            logger.info("Login exitoso")
            return True

        except TimeoutException:
            logger.error("Timeout durante el login")
            return False
        except Exception as e:
            logger.error(f"Error durante el login: {str(e)}")
            return False

    def get_subjects(self):
        """Obtiene la lista de todas las asignaturas de matemáticas"""
        try:
            logger.info("Obteniendo lista de asignaturas...")
            url = f"{self.base_url}/docencia/horarios/indiceplan/20261/217"
            self.driver.get(url)

            # Esperar a que cargue la tabla de asignaturas
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/docencia/horarios/20261/217/')]")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            subject_links = []

            # Encontrar todos los enlaces de asignaturas
            links = soup.find_all("a", href=re.compile(r"/docencia/horarios/20261/217/\d+"))
            for link in links:
                subject_name = link.get_text().strip()
                # Limpiar el nombre (remover "X grupos")
                subject_name = re.sub(r",\s*\d+\s*grupos?", "", subject_name)
                href = link["href"]
                subject_id = re.search(r"/(\d+)$", href).group(1)

                subject_links.append({"name": subject_name, "url": f"{self.base_url}{href}", "id": subject_id})

            logger.info(f"Encontradas {len(subject_links)} asignaturas")
            return subject_links

        except Exception as e:
            logger.error(f"Error obteniendo asignaturas: {str(e)}")
            return []

    def get_professors_from_subject(self, subject_url, subject_name):
        """Obtiene todos los profesores de una asignatura específica"""
        try:
            self.driver.get(subject_url)

            # Esperar a que cargue la página de grupos
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/directorio/')]")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            professor_links = []

            # Encontrar todos los enlaces a perfiles de profesores
            links = soup.find_all("a", href=re.compile(r"/directorio/\d+"))
            for link in links:
                # Verificar que sea un enlace de profesor (no de ayudante)
                parent_text = link.find_parent().get_text() if link.find_parent() else ""
                if "Profesor" in parent_text and "Ayudante" not in parent_text:
                    href = link["href"]
                    professor_id = re.search(r"/(\d+)$", href).group(1)
                    professor_name = link.get_text().strip()

                    professor_links.append({"name": professor_name, "url": f"{self.base_url}{href}", "id": professor_id, "source_subject": subject_name})

            return professor_links

        except Exception as e:
            logger.error(f"Error obteniendo profesores de {subject_name}: {str(e)}")
            return []

    def extract_professor_data(self, professor_url, source_subject):
        """Extrae los datos completos de un profesor"""
        try:
            self.driver.get(professor_url)

            # Esperar a que cargue la página del profesor
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Extraer nombre
            name_element = soup.find("h1")
            name = name_element.get_text().strip() if name_element else ""

            # Extraer email
            email = ""
            email_element = soup.find("a", href=re.compile(r"^mailto:"))
            if email_element:
                email = email_element["href"].replace("mailto:", "").strip()

            # Extraer todas las materias que imparte
            all_subjects = self._extract_all_subjects(soup)

            # Crear estructura de datos según el esquema requerido
            professor_data = {
                "name": name,
                "email": email,
                "subject": source_subject,  # La materia que nos llevó a este profesor
                "otherSubjects": [s for s in all_subjects if s != source_subject],
                "infoAboutPersonalWork": "",
                "isComplexAnalysis": self._is_complex_analysis(all_subjects),
                "wasEmailSend": False,
                "sourceUrl": professor_url,
                "scrapedAt": time.time(),
            }

            logger.info(f"Datos extraídos para: {name}")
            return professor_data

        except Exception as e:
            logger.error(f"Error extrayendo datos de {professor_url}: {str(e)}")
            return None

    def _extract_all_subjects(self, soup):
        """Extrae todas las materias que imparte el profesor"""
        subjects = []

        # Buscar en la sección de enseñanza
        teaching_section = soup.find("h2", string=re.compile("Enseñanza"))
        if teaching_section:
            # Buscar en los elementos siguientes
            current_element = teaching_section.find_next_sibling()
            while current_element and current_element.name not in ["h2", "h3"]:
                if current_element.name == "ul":
                    # Extraer materias de listas
                    for li in current_element.find_all("li"):
                        text = li.get_text().strip()
                        # Extraer solo el nombre de la materia (antes de la coma)
                        subject_match = re.search(r"^([^,]+)", text)
                        if subject_match:
                            subject_name = subject_match.group(1).strip()
                            if subject_name and subject_name not in subjects:
                                subjects.append(subject_name)
                elif current_element.name == "p":
                    # Buscar materias en párrafos
                    text = current_element.get_text()
                    subject_matches = re.findall(r"([^,]+),\s*Profesor", text)
                    subjects.extend([s.strip() for s in subject_matches if s.strip()])

                current_element = current_element.find_next_sibling()

        return list(set(subjects))  # Remover duplicados

    def _is_complex_analysis(self, subjects):
        """Determina si el profesor imparte Análisis Complejo"""
        complex_keywords = ["Variable Compleja", "Variable Compleja I", "Variable Compleja II", "Análisis Complejo", "Funciones Complejas"]

        return any(any(keyword in subject for keyword in complex_keywords) for subject in subjects)

    def scrape_all_professors(self):
        """Función principal que obtiene todos los profesores"""
        self.setup_driver()

        try:
            if not self.login():
                raise Exception("No se pudo realizar el login")

            # Obtener todas las asignaturas
            subjects = self.get_subjects()
            all_professors = []
            processed_professors = set()  # Para evitar duplicados por email

            for subject in subjects:
                logger.info(f"Procesando asignatura: {subject['name']}")

                # Obtener profesores de esta asignatura
                professors = self.get_professors_from_subject(subject["url"], subject["name"])

                for professor in professors:
                    # Extraer datos del profesor
                    professor_data = self.extract_professor_data(professor["url"], subject["name"])

                    if professor_data and professor_data["email"] and professor_data["email"] not in processed_professors:

                        all_professors.append(professor_data)
                        processed_professors.add(professor_data["email"])

                    time.sleep(1)  # Respeta el servidor

                time.sleep(2)  # Pausa más larga entre asignaturas

            return all_professors

        finally:
            if self.driver:
                self.driver.quit()
