# Envío Automático de Emails a Profesores

Este proyecto es una aplicación de consola en Python diseñada para enviar correos electrónicos personalizados a profesores de forma automatizada. Utiliza plantillas para el asunto y el cuerpo del mensaje, y obtiene los datos de los destinatarios desde una base de datos TimescaleDB.

## Características

- **Envío de correos electrónicos**: Se conecta a un servidor SMTP para enviar los correos.
- **Personalización**: Utiliza plantillas para el asunto y el cuerpo del correo, permitiendo un alto grado de personalización.
- **Base de datos**: Se integra con TimescaleDB (PostgreSQL) para gestionar la lista de profesores y el estado de los envíos.
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
    # Configuración de la base de datos TimescaleDB/PostgreSQL
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=teachers

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
    Asegúrate de que tu instancia de TimescaleDB esté en funcionamiento. Puedes usar Docker para levantar una base de datos rápidamente:
    ```bash
    docker-compose up -d
    ```

    Luego, puedes usar un cliente de PostgreSQL para conectarte a la base de datos y ejecutar el DDL que se encuentra en la sección de "Estructura de Datos" para crear la tabla `teachers`.

2.  **Ejecutar la aplicación**:
    Una vez que la base de datos esté poblada y el archivo `.env` configurado, puedes ejecutar la aplicación:
    ```bash
    python main.py
    ```
    La aplicación buscará todos los profesores en la tabla que no hayan recibido un correo (`wasEmailSend: false`), se los enviará y actualizará su estado.

## Estructura de Datos

El schema SQL (DDL) para la nueva tabla `teachers` en TimescaleDB es el siguiente:

```sql
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    subject VARCHAR(255),
    otherSubjects TEXT[],
    infoAboutPersonalWork TEXT,
    isComplexAnalysis BOOLEAN,
    wasEmailSend BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convertir la tabla en una hypertable (característica de TimescaleDB)
SELECT create_hypertable('teachers', 'created_at');
```

## Scripts Adicionales

-   **Backup de la base de datos**:
    Para crear un backup de tu base de datos, puedes usar `pg_dump`:
    ```bash
    docker-compose exec -T timescaledb pg_dump -U user -d teachers > backup.sql
    ```

-   **Restaurar la base de datos**:
    Para restaurar una base de datos desde un backup, primero asegúrate de que el contenedor de Docker esté corriendo. Luego, puedes usar `psql`:
    ```bash
    cat backup.sql | docker-compose exec -T timescaledb psql -U user -d teachers
    ```
