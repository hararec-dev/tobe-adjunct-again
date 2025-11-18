import logging
import time

import requests
from bs4 import BeautifulSoup
from decouple import config
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FacultadScraper:
    def __init__(self, headless=True):
        self.base_url = config("FACULTAD_URL")
        self.username = config("FACULTAD_USERNAME")
        self.password = config("FACULTAD_PASSWORD")
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

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

    def login(self):
        """Realiza el login en el portal de la facultad"""
        try:
            self.driver.get(f"{self.base_url}/login")

            # Esperar a que cargue el formulario de login
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))

            # Llenar credenciales
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)

            # Enviar formulario
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Esperar a que se complete el login
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))

            # Guardar cookies para requests
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie["name"], cookie["value"])

            self.logger.info("Login exitoso")
            return True

        except TimeoutException:
            self.logger.error("Timeout durante el login")
            return False
        except Exception as e:
            self.logger.error(f"Error durante el login: {str(e)}")
            return False

    def get_department_links(self):
        """Obtiene los enlaces a los departamentos"""
        try:
            self.driver.get(f"{self.base_url}/departamentos")

            # Esperar a que cargue la lista de departamentos
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "department-list")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            department_links = []

            # Buscar enlaces de departamentos (ajusta los selectores según tu portal)
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if "/departamento/" in href or "/department/" in href:
                    department_links.append(f"{self.base_url}{href}")

            self.logger.info(f"Encontrados {len(department_links)} departamentos")
            return department_links

        except Exception as e:
            self.logger.error(f"Error obteniendo departamentos: {str(e)}")
            return []

    def extract_professor_data(self, professor_url):
        """Extrae datos de un profesor específico"""
        try:
            self.driver.get(professor_url)

            # Esperar a que cargue la página del profesor
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "professor-profile")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Extraer información básica (ajusta los selectores)
            name = self._extract_text(soup, ".professor-name, h1.name")
            email = self._extract_text(soup, '.email, a[href^="mailto:"]')

            # Extraer materias que imparte
            subjects = self._extract_subjects(soup)

            # Extraer información de especialización
            specialization = self._extract_specialization(soup)

            # Determinar si imparte Análisis Complejo
            is_complex_analysis = self._check_complex_analysis(subjects, specialization)

            professor_data = {
                "name": name,
                "email": email,
                "subject": (subjects[0] if subjects else "Matemáticas"),  # Materia principal
                "otherSubjects": subjects[1:] if len(subjects) > 1 else [],
                "infoAboutPersonalWork": specialization,
                "isComplexAnalysis": is_complex_analysis,
                "wasEmailSend": False,
                "sourceUrl": professor_url,
                "scrapedAt": time.time(),
            }

            self.logger.info(f"Datos extraídos para: {name}")
            return professor_data

        except Exception as e:
            self.logger.error(f"Error extrayendo datos de {professor_url}: {str(e)}")
            return None

    def _extract_text(self, soup, selector):
        """Extrae texto usando un selector CSS"""
        try:
            element = soup.select_one(selector)
            if element:
                # Para emails, extraer del href si es un mailto
                if selector == '.email, a[href^="mailto:"]' and element.get("href", "").startswith("mailto:"):
                    return element["href"].replace("mailto:", "").strip()
                return element.get_text().strip()
            return ""
        except:
            return ""

    def _extract_subjects(self, soup):
        """Extrae la lista de materias que imparte el profesor"""
        subjects = []

        # Buscar en diferentes ubicaciones comunes
        subject_selectors = [
            ".subjects-list li",
            ".courses-taught li",
            ".materias li",
            ".asignaturas li",
        ]

        for selector in subject_selectors:
            elements = soup.select(selector)
            for element in elements:
                subject = element.get_text().strip()
                if subject and subject not in subjects:
                    subjects.append(subject)

        return subjects

    def _extract_specialization(self, soup):
        """Extrae información sobre especialización/investigación"""
        specialization_selectors = [
            ".research-interests",
            ".specialization",
            ".area-interes",
            ".bio .description",
        ]

        for selector in specialization_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()[:500]  # Limitar longitud

        return ""

    def _check_complex_analysis(self, subjects, specialization):
        """Determina si el profesor imparte Análisis Complejo"""
        complex_analysis_keywords = [
            "análisis complejo",
            "analisis complejo",
            "variable compleja",
            "complex analysis",
            "complex variable",
            "funciones complejas",
        ]

        # Buscar en materias
        for subject in subjects:
            if any(keyword in subject.lower() for keyword in complex_analysis_keywords):
                return True

        # Buscar en especialización
        if any(keyword in specialization.lower() for keyword in complex_analysis_keywords):
            return True

        return False

    def get_all_professors(self):
        """Obtiene datos de todos los profesores"""
        self.setup_driver()

        try:
            if not self.login():
                raise Exception("No se pudo realizar el login")

            department_links = self.get_department_links()
            all_professors = []

            for dept_link in department_links:
                self.logger.info(f"Procesando departamento: {dept_link}")
                professor_links = self._get_professor_links_from_department(dept_link)

                for prof_link in professor_links:
                    professor_data = self.extract_professor_data(prof_link)
                    if professor_data and professor_data["email"]:
                        all_professors.append(professor_data)
                    time.sleep(1)  # Respeta el servidor

            return all_professors

        finally:
            if self.driver:
                self.driver.quit()

    def _get_professor_links_from_department(self, department_url):
        """Obtiene enlaces a perfiles de profesores desde un departamento"""
        try:
            self.driver.get(department_url)

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "professor-list")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            professor_links = []

            # Buscar enlaces a perfiles de profesores
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                text = link.get_text().strip()
                # Filtrar enlaces que probablemente sean perfiles
                if ("/profesor/" in href or "/professor/" in href or "/academic/" in href) and text:
                    full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                    professor_links.append(full_url)

            return list(set(professor_links))  # Remover duplicados

        except Exception as e:
            self.logger.error(f"Error obteniendo profesores de {department_url}: {str(e)}")
            return []
