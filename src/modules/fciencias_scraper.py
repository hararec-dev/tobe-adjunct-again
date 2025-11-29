import logging
import re
import time

import requests
from bs4 import BeautifulSoup
from decouple import config
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class FcienciasScraper:
    def __init__(self, headless=True):
        self.base_url = config("FCIENCIAS_BASE_URL")
        self.username = config("FCIENCIAS_USERNAME")
        self.password = config("FCIENCIAS_PASSWORD")
        self.wait_timeout = config("WAIT_TIMEOUT", default=30, cast=int)  # Aumentado a 30 segundos
        self.headless = headless
        self.driver = None
        self.wait = None

    def setup_driver(self):
        """Configura el WebDriver para Selenium con mejores opciones"""
        try:
            options = webdriver.ChromeOptions()

            if self.headless:
                options.add_argument("--headless=new")  # Nueva sintaxis para headless
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Inicializar driver con manejo de errores
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Configurar tiempo de espera de página
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)

            logger.info("WebDriver configurado exitosamente")
            return True

        except WebDriverException as e:
            logger.error(f"Error configurando WebDriver: {str(e)}")
            logger.error("Asegúrate de que ChromeDriver esté instalado y en el PATH")
            return False
        except Exception as e:
            logger.error(f"Error inesperado configurando WebDriver: {str(e)}")
            return False

    def check_website_availability(self):
        """Verifica si el sitio web está disponible"""
        try:
            response = requests.get(self.base_url, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"El sitio web no está disponible: {str(e)}")
            return False

    def login(self):
        """Realiza el login en el portal de la facultad con múltiples estrategias"""
        try:
            logger.info("Iniciando sesión en el portal...")

            # Verificar disponibilidad del sitio
            if not self.check_website_availability():
                raise Exception("El sitio web no está disponible")

            # Navegar a la página de login
            self.driver.get(f"{self.base_url}/acceder")
            logger.info("Página de login cargada")

            # ESTRATEGIA 1: Esperar por el formulario de login
            try:
                login_form = self.wait.until(EC.presence_of_element_located((By.ID, "loginForm")))
                logger.info("Formulario de login encontrado por ID")
            except TimeoutException:
                # ESTRATEGIA 2: Buscar por name si ID falla
                logger.warning("Formulario no encontrado por ID, intentando por name...")
                login_form = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                logger.info("Campo de usuario encontrado por name")

            # Llenar campos de login con múltiples selectores
            username_field = None
            password_field = None

            # Intentar diferentes selectores para username
            selectors = [(By.ID, "username"), (By.NAME, "username"), (By.XPATH, "//input[@name='username']"), (By.CSS_SELECTOR, "input[name='username']")]

            for by, selector in selectors:
                try:
                    username_field = self.driver.find_element(by, selector)
                    logger.info(f"Campo usuario encontrado con {by}: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if not username_field:
                raise NoSuchElementException("No se pudo encontrar el campo de usuario")

            # Intentar diferentes selectores para password
            for by, selector in [(By.ID, "password"), (By.NAME, "password"), (By.XPATH, "//input[@type='password']")]:
                try:
                    password_field = self.driver.find_element(by, selector)
                    logger.info(f"Campo contraseña encontrado con {by}: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if not password_field:
                raise NoSuchElementException("No se pudo encontrar el campo de contraseña")

            # Limpiar y llenar campos
            username_field.clear()
            username_field.send_keys(self.username)

            password_field.clear()
            password_field.send_keys(self.password)

            logger.info("Credenciales ingresadas")

            # Buscar botón de login con múltiples selectores
            login_button = None
            for by, selector in [
                (By.ID, "submit_0"),
                (By.NAME, "submit_0"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Acceder')]"),
                (By.CSS_SELECTOR, "input[value='Acceder']"),
            ]:
                try:
                    login_button = self.driver.find_element(by, selector)
                    logger.info(f"Botón de login encontrado con {by}: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if not login_button:
                raise NoSuchElementException("No se pudo encontrar el botón de login")

            # Hacer click en el botón
            login_button.click()
            logger.info("Botón de login presionado")

            # Esperar redirección después del login
            self.wait.until(EC.url_changes(f"{self.base_url}/acceder"))
            logger.info("Redirección después del login detectada")

            # Verificar login exitoso
            time.sleep(3)  # Pausa para asegurar que la página cargue

            # Verificar que no estamos en la página de login
            if "acceder" in self.driver.current_url:
                # Verificar si hay mensaje de error
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "x-error")
                    if error_elements:
                        error_text = error_elements[0].text
                        logger.error(f"Error de login: {error_text}")
                        return False
                except:
                    pass

                logger.error("El login falló - todavía en página de login")
                return False

            logger.info("Login exitoso")
            return True

        except TimeoutException as e:
            logger.error(f"Timeout durante el login: {str(e)}")
            logger.info("Intentando estrategia alternativa...")
            return self._alternative_login_strategy()
        except NoSuchElementException as e:
            logger.error(f"Elemento no encontrado durante el login: {str(e)}")
            # Tomar screenshot para debugging
            self._take_screenshot("login_error")
            return False
        except Exception as e:
            logger.error(f"Error inesperado durante el login: {str(e)}")
            self._take_screenshot("login_unexpected_error")
            return False

    def _alternative_login_strategy(self):
        """Estrategia alternativa para login usando JavaScript"""
        try:
            logger.info("Intentando estrategia alternativa de login...")

            # Usar JavaScript para llenar los campos
            self.driver.execute_script(
                f"""
                document.getElementById('username').value = '{self.username}';
                document.getElementById('password').value = '{self.password}';
                document.getElementById('submit_0').click();
            """
            )

            time.sleep(5)  # Esperar después del click JavaScript

            if "acceder" not in self.driver.current_url:
                logger.info("Login exitoso con estrategia alternativa")
                return True
            else:
                logger.error("Estrategia alternativa falló")
                return False

        except Exception as e:
            logger.error(f"Estrategia alternativa falló: {str(e)}")
            return False

    def _take_screenshot(self, name):
        """Toma un screenshot para debugging"""
        try:
            screenshot_path = f"{name}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot guardado: {screenshot_path}")
        except Exception as e:
            logger.error(f"No se pudo tomar screenshot: {str(e)}")

    def scrape_all_professors(self, max_subjects=None):
        """Función principal que obtiene todos los profesores"""
        # Configurar driver
        if not self.setup_driver():
            raise Exception("No se pudo configurar WebDriver")

        try:
            # Intentar login
            if not self.login():
                raise Exception("No se pudo realizar el login")

            # Obtener todas las asignaturas
            subjects = self.get_subjects()
            if not subjects:
                raise Exception("No se pudieron obtener las asignaturas")

            # Limitar para pruebas si se especifica
            if max_subjects:
                subjects = subjects[:max_subjects]
                logger.info(f"MODO PRUEBA: Procesando {max_subjects} asignaturas")

            all_professors = []
            processed_emails = set()

            total_subjects = len(subjects)

            for i, subject in enumerate(subjects, 1):
                logger.info(f"[{i}/{total_subjects}] Procesando: {subject['name']}")

                # Obtener profesores de esta asignatura
                professors = self.get_professors_from_subject(subject["url"], subject["name"])

                for professor in professors:
                    # Extraer datos del profesor
                    professor_data = self.extract_professor_data(professor["url"], subject["name"])

                    if professor_data and professor_data["email"] and professor_data["email"] not in processed_emails:

                        all_professors.append(professor_data)
                        processed_emails.add(professor_data["email"])
                        logger.info(f"  Agregado: {professor_data['name']}")

                    time.sleep(2)  # Respeta el servidor

                time.sleep(3)  # Pausa más larga entre asignaturas

                # Break early if in test mode with max_subjects
                if max_subjects and i >= max_subjects:
                    break

            logger.info(f"Proceso completado. Total de profesores únicos: {len(all_professors)}")
            return all_professors

        except Exception as e:
            logger.error(f"Error en el proceso de scraping: {str(e)}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver cerrado")

    # Los métodos get_subjects, get_professors_from_subject, extract_professor_data, etc.
    # se mantienen igual que en la versión anterior
    def get_subjects(self):
        """Obtiene la lista de todas las asignaturas de matemáticas"""
        try:
            logger.info("Obteniendo lista de asignaturas...")
            url = f"{self.base_url}/docencia/horarios/indiceplan/20261/217"
            self.driver.get(url)

            # Esperar a que cargue el contenido principal
            self.wait.until(EC.presence_of_element_located((By.ID, "info-contenido")))

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
            self.wait.until(EC.presence_of_element_located((By.ID, "info-contenido")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            professor_links = []

            # ESTRATEGIA MEJORADA: Buscar por estructura de tabla específica
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        first_cell_text = cells[0].get_text().strip()
                        if first_cell_text == "Profesor":
                            professor_link = cells[1].find("a", href=re.compile(r"/directorio/\d+"))
                            if professor_link:
                                professor_name = professor_link.get_text().strip()
                                href = professor_link["href"]
                                professor_id = re.search(r"/(\d+)$", href).group(1)

                                professor_links.append({"name": professor_name, "url": f"{self.base_url}{href}", "id": professor_id, "source_subject": subject_name})
                                break

            logger.info(f"Encontrados {len(professor_links)} profesores en {subject_name}")
            return professor_links

        except Exception as e:
            logger.error(f"Error obteniendo profesores de {subject_name}: {str(e)}")
            return []

    def extract_professor_data(self, professor_url, source_subject):
        """Extrae los datos completos de un profesor"""
        try:
            self.driver.get(professor_url)

            # Esperar a que cargue la página del profesor
            self.wait.until(EC.presence_of_element_located((By.ID, "info-contenido")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Extraer nombre
            name_element = soup.find("h1")
            name = name_element.get_text().strip() if name_element else ""

            # Extraer email
            email = ""
            email_elements = soup.find_all("a", href=re.compile(r"^mailto:"))
            for email_element in email_elements:
                email = email_element["href"].replace("mailto:", "").strip()
                if email:
                    break

            # Extraer todas las materias que imparte
            all_subjects = self._extract_all_subjects(soup)

            professor_data = {
                "name": name,
                "email": email,
                "subject": source_subject,
                "otherSubjects": [s for s in all_subjects if s != source_subject],
                "infoAboutPersonalWork": "",
                "isComplexAnalysis": self._is_complex_analysis(all_subjects),
                "wasEmailSend": False,
                "sourceUrl": professor_url,
                "scrapedAt": time.time(),
            }

            if email:
                logger.info(f"Datos extraídos para: {name} - {email}")
            else:
                logger.warning(f"Profesor sin email: {name}")

            return professor_data

        except Exception as e:
            logger.error(f"Error extrayendo datos de {professor_url}: {str(e)}")
            return None

    def _extract_all_subjects(self, soup):
        """Extrae todas las materias que imparte el profesor"""
        subjects = []

        enseñanza_headers = soup.find_all(["h2", "h3"], string=re.compile("Enseñanza"))

        for header in enseñanza_headers:
            current_element = header.find_next_sibling()
            while current_element and current_element.name not in ["h1", "h2", "h3"]:
                if current_element.name == "div":
                    subject_links = current_element.find_all("a", href=re.compile(r"/docencia/horarios/detalles/\d+"))

                    for link in subject_links:
                        link_text = link.get_text().strip()
                        subject_name = re.sub(r",\s*Profesor.*$", "", link_text).strip()
                        if subject_name and subject_name not in subjects:
                            subjects.append(subject_name)

                current_element = current_element.find_next_sibling()

        return list(set(subjects))

    def _is_complex_analysis(self, subjects):
        """Determina si el profesor imparte Análisis Complejo"""
        complex_keywords = ["Variable Compleja I", "Variable Compleja II", "Variable Compleja", "Análisis Complejo", "Funciones Complejas"]

        for subject in subjects:
            if any(keyword.lower() in subject.lower() for keyword in complex_keywords):
                return True
        return False
