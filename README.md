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