# **Sistema Automatizado - Recopilación de Datos y Envío de Emails**

![Logo UNAM](https://web.fciencias.unam.mx/assets/meta/66c61fb/layout/encabezado-unam.gif)

Este proyecto es una aplicación de consola en Python diseñada para alumnos de la facultad de ciencias UNAM, y automatiza el envío de correos electrónicos personalizados a profesores. Utiliza **web scraping** para recopilar datos de profesores y almacena la información en una base de datos **MongoDB**. Luego, envía emails masivos utilizando plantillas personalizables.

-----

## Prerrequisitos

  * Python 3.8+
  * Docker
  * ChromeDriver (para web scraping)
  * Cuenta Oficial de la UNAM

-----

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/hararec-dev/tobe-adjunct-again.git
cd tobe-adjunct-again
```

### 2. Configurar entorno virtual

```bash
# Instalar pipenv si no está disponible
pip install pipenv
# Crear y activar entorno virtual
pipenv shell
# Instalar dependencias
pipenv install
```

### 3. Configurar variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```ini
# Configuración de MongoDB
MONGO_USERNAME=admin
MONGO_PASSWORD=tu_contraseña_mongo
MONGO_PORT=8001
MONGO_HOST=localhost
MONGO_DATABASE=teachers
MONGO_COLLECTION=development

# Configuración de Email (Gmail)
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicación
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465

# Configuración de Scraping - FCIENCIAS
FCIENCIAS_USERNAME=tu_numero_de_cuenta
FCIENCIAS_PASSWORD=tu_contraseña_fciencias
FCIENCIAS_BASE_URL=https://web.fciencias.unam.mx
WAIT_TIMEOUT=30
OPEN_BROWSER=False
REQUEST_DELAY=2
```

### 4. Configurar credenciales de Gmail

**Para habilitar el envío desde Gmail:**

1.  **Habilitar Verificación en Dos Pasos**

      * Ve a [tu Cuenta de Google](https://myaccount.google.com/)
      * Navega a: Seguridad → Verificación en Dos Pasos
      * Activa la verificación

2.  **Generar Contraseña de Aplicación**

      * En la misma sección de Seguridad, busca "**Contraseñas de Aplicaciones**"
      * Selecciona "Aplicación": **Otra**
      * Ingresa nombre: `Script de Email Python`
      * Copia la contraseña generada de 16 dígitos y úsala en `EMAIL_PASSWORD`

-----

## Uso

### Iniciar base de datos con Docker

```bash
docker-compose up -d
```

### Ejecutar Scraping de Profesores

```bash
# Scraping completo (todas las asignaturas)
python scrape_fciencias.py
# Scraping con opciones avanzadas
python scrape_fciencias.py --test 5 --delay 3 --no-headless
```

### Envío de Emails

```bash
# Solo envío de emails
python main.py
# Scraping y luego envío de emails
python main.py --scrape
# Solo scraping
python main.py --scrape-only
# Modo prueba con navegador visible
python main.py --scrape-only --test --no-headless
```

-----

## Estructura de Datos

Cada profesor en la base de datos tiene la siguiente estructura:

```json
{
    "name": "Dr. Juan José Alba González",
    "email": "math@ciencias.unam.mx",
    "subject": "Teoría de los Números I",
    "otherSubjects": [
        "Álgebra Superior I",
        "Álgebra Superior II",
        "Seminario de Análisis Combinatorio"
    ],
    "infoAboutPersonalWork": "",
    "isComplexAnalysis": false,
    "wasEmailSend": false,
    "sourceUrl": "https://web.fciencias.unam.mx/directorio/32808",
    "scrapedAt": 1637891234.567890
}
```

-----

## Scripts Adicionales

### Backup de Base de Datos

```bash
chmod +x ./backup-mongodb.sh
./backup-mongodb.sh
```

### Restaurar Base de Datos

```bash
docker-compose up -d
chmod +x ./restore-mongodb.sh
./restore-mongodb.sh <timestamp_del_backup>
# Ejemplo: ./restore-mongodb.sh 20231127_120000
```

-----

## Configuración de Scraping

### Opciones disponibles:

  * `--test N`: Procesar solo N asignaturas (modo prueba)
  * `--no-headless`: Ejecutar con navegador visible
  * `--delay SECONDS`: Delay entre requests (default: 2)
  * `--scrape-only`: Solo scraping, sin enviar emails

### Características del Scraper:

  * Login automático al portal FCIENCIAS
  * Detección y manejo de sesiones expiradas
  * Extracción robusta de nombres, emails y materias
  * Limpieza automática de datos (remueve "Ayudante", "Profesor")
  * Manejo de errores y reintentos automáticos
  * Delays configurables para respetar el servidor

-----

## Solución de Problemas

### Problemas comunes de ChromeDriver:

```bash
# Verificar instalación
which chromedriver
chromedriver --version
# Instalar en macOS
brew install chromedriver
# Instalar en Linux (Ubuntu/Debian)
sudo apt install chromium-chromedriver
```

### Error de login en scraping:

  * Verifica credenciales en `.env`
  * Ejecuta con `OPEN_BROWSER=True` para debugging
  * Verifica que el portal esté accesible manualmente

### Error de envío de emails:

  * Verifica configuración de Gmail
  * Confirma que la verificación en 2 pasos esté activada
  * Usa **contraseña de aplicación**, no la contraseña personal

-----

## Contribución

Las contribuciones son bienvenidas. Por favor:

1.  Fork el proyecto
2.  Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3.  Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4.  Push a la rama (`git push origin feature/AmazingFeature`)
5.  Abre un Pull Request

-----

## Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](./LICENSE) para más detalles.