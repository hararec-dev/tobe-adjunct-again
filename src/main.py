import json
from pathlib import Path
from modules.email_sender import EmailSender

def main():
    email_sender = EmailSender()
    data_path = Path('src/data/json/teachers.json')
    
    with open(data_path, 'r', encoding='utf-8') as f:
        teachers = json.load(f)['teachers']
    
    for teacher in teachers:
        try:
            email_sender.send_email(teacher)
            print(f"Email enviado a {teacher['email']}")
        except Exception as e:
            print(f"Error enviando a {teacher['email']}: {str(e)}")

if __name__ == "__main__":
    main()