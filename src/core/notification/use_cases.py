import time

from src.core.notification.services import EmailSender
from src.core.persistance.repository import ProfessorRepository


def send_emails():
    """Envía emails a profesores"""
    email_sender = EmailSender()
    repository = ProfessorRepository()

    teachers = repository.get_professors_to_email()
    start_time = time.time()

    try:
        email_sender.connect()
        sent_count = 0

        for teacher in teachers:
            try:
                email_sender.send_email(teacher, use_existing_connection=True)
                repository.update_professor_email_status(teacher["_id"])
                print(f"Email enviado a {teacher['email']}")
                sent_count += 1
            except Exception as e:
                print(f"Error enviando a {teacher['email']}: {str(e)}")
    finally:
        email_sender.disconnect()
        repository.close()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nSe enviaron {sent_count} emails en {execution_time:.2f} segundos")
