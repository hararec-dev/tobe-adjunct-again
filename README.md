# Envío Automático de Emails a Profesores

Este proyecto es una aplicación de consola en Python diseñada para enviar correos electrónicos personalizados a profesores de forma automatizada. Utiliza plantillas para el asunto y el cuerpo del mensaje, y obtiene los datos de los destinatarios desde una base de datos MongoDB.

## Características

- **Envío de correos electrónicos**: Se conecta a un servidor SMTP para enviar los correos.
- **Personalización**: Utiliza plantillas para el asunto y el cuerpo del correo, permitiendo un alto grado de personalización.
- **Base de datos**: Se integra con MongoDB para gestionar la lista de profesores y el estado de los envíos.
- **Manejo de estado**: Realiza un seguimiento de los correos enviados para evitar duplicados.

## Configuración del Entorno

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/hararec-dev/tobe-adjunct-again.git
    cd tobe-adjunct-again
    ```

2.  **Crear un entorno virtual con pipenv (recomendado)**:
    ```bash
    pip install pipenv
    pipenv shell
    ```

3.  **Instalar las dependencias**:
    ```bash
    pipenv install
    ```

4.  **Configurar las variables de entorno**:
    Crea un archivo `.env` en la raíz del proyecto, basándote en el archivo `.env.example`. Deberás completar los siguientes valores:

    ```ini
    # Configuración de la base de datos MongoDB
    # la cadena de conexión es la siguiente:
    # mongodb://admin:mTQOL70fs3rJ@localhost:8001/teachers?authSource=admin
    MONGO_USERNAME=admin
    MONGO_PASSWORD=mTQOL70fs3rJ
    MONGO_PORT=8001
    MONGO_HOST=localhost
    MONGO_DATABASE=teachers
    MONGO_COLLECTION=development

    # Configuración del servidor de correo (SMTP)
    EMAIL_SERVER=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USER=tu_correo@gmail.com
    EMAIL_PASSWORD=tu_contraseña_de_aplicacion
    ```

    **Nota sobre la contraseña de Gmail**: Para habilitar el envío de correos desde una cuenta de Gmail, es necesario generar una "Contraseña de Aplicación". Sigue estos pasos:
1. **Habilitar Verificación en Dos Pasos**
   - Ve a [tu Cuenta de Google](https://myaccount.google.com/)
   - Navega a: Seguridad → Verificación en Dos Pasos
   - Haz clic en "ACTIVAR"

2. **Crear una "Contraseña de Aplicación"**
   - Permanece en la sección de Seguridad
   - Busca "Contraseñas de Aplicaciones"
   - Sigue estos pasos:
     1. Selecciona Aplicación: Otra
     2. Ingresa Nombre: Script de Email Python
     3. Copia la contraseña generada de 16 dígitos

## Uso

1.  **Poblar la base de datos**:
    Asegúrate de que tu instancia de MongoDB esté en funcionamiento. Puedes usar Docker para levantar una base de datos rápidamente:
    ```bash
    docker-compose up -d
    ```

    Luego, puedes usar el script `scripts/data.js` para insertar un dato de ejemplo en la colección `teachers`. Este script te servirá como guía para entender la estructura de datos necesaria.
    ```bash
    mongo email_sender scripts/data.js
    ```

2.  **Ejecutar la aplicación**:
    Una vez que la base de datos esté poblada y el archivo `.env` configurado, puedes ejecutar la aplicación:
    ```bash
    python main.py
    ```
    La aplicación buscará todos los profesores en la colección que no hayan recibido un correo (`wasEmailSend: false`), se los enviará y actualizará su estado.

## Estructura de Datos

El documento de cada profesor en la colección de MongoDB debe tener la siguiente estructura:

```javascript
{
    name: "Nombre del Profesor",
    email: "correo@ejemplo.com",
    subject: "Asunto Principal del Correo",
    otherSubjects: [
        "Otra Materia 1",
        "Otra Materia 2"
    ],
    infoAboutPersonalWork: "Información sobre su especialización",
    isComplexAnalysis: true, // o false
    wasEmailSend: false
}
```

## Scripts Adicionales

-   **Backup de la base de datos**:
    Para crear un backup de tu base de datos, asegúrate de que el script sea ejecutable y luego córrelo:
    ```bash
    chmod +x ./backup-mongodb.sh
    ./backup-mongodb.sh
    ```

-   **Restaurar la base de datos**:
    Para restaurar una base de datos desde un backup, primero asegúrate de que el contenedor de Docker esté corriendo. Luego, ejecuta el script de restauración con el timestamp del backup que deseas usar.
    ```bash
    docker-compose up -d
    chmod +x ./restore-mongodb.sh
    ./restore-mongodb.sh <timestamp_del_backup>
    ```
    Por ejemplo: `./restore-mongodb.sh 20230815_120000`

-   **Scraping de profesores**:
    ```bash
    # Solo scraping
    python main.py --scrape-only

    # Scraping y luego envío de emails
    python main.py --scrape

    # Solo envío de emails (comportamiento original)
    python main.py

    # O usar el script dedicado
    python scrape_fciencias.py
    ```
