# Envío Automático de Emails

Este proyecto permite enviar emails de forma automatizada a profesores, personalizando el asunto y el cuerpo del mensaje utilizando plantillas de texto y datos extraídos de un archivo JSON.

## Arquitetura

```bash
/
├── .env
├── .gitignore
└── src/
    ├── main.py
    ├── config/
    │   └── settings.py
    ├── data/
    │   └── json/
    │       └── teachers.json
    ├── templates/
    │   ├── message_woman.txt
    │   ├── message_man.txt
    │   └── subject.txt
    └── modules/
        ├── email_sender.py
        └── template_loader.py
```

## Habilitar envío automático desde Gmail

### Guía Paso a Paso

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
