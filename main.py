import time
from src.modules.email_sender import EmailSender
from src.services.timescaledb import get_connection, get_unsent_teachers, mark_teacher_as_sent

def main():
    email_sender = EmailSender()
    conn = get_connection()
    
    try:
        teachers_data = get_unsent_teachers(conn)

        teachers = [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "subject": row[3],
                "otherSubjects": row[4],
                "infoAboutPersonalWork": row[5],
                "isComplexAnalysis": row[6]
            }
            for row in teachers_data
        ]

        start_time = time.time()

        email_sender.connect()
        sent_count = 0
        
        for teacher in teachers:
            try:
                email_sender.send_email(teacher, use_existing_connection=True)
                mark_teacher_as_sent(conn, teacher['id'])
                print(f"Email enviado a {teacher['email']}")
                sent_count += 1
            except Exception as e:
                print(f"Error enviando a {teacher['email']}: {str(e)}")
    finally:
        email_sender.disconnect()
        conn.close()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nSe enviaron {sent_count} emails en {execution_time:.2f} segundos")

if __name__ == "__main__":
    main()
