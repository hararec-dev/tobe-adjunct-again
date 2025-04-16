from src.modules.email_sender import EmailSender
from src.config.settings import MONGO_CONFIG
from pymongo import MongoClient

def main():
    email_sender = EmailSender()
    client = MongoClient(
        host=MONGO_CONFIG['host'],
        port=MONGO_CONFIG['port'],
        username=MONGO_CONFIG['username'],
        password=MONGO_CONFIG['password']
    )
    
    db = client[MONGO_CONFIG['database']]
    collection = db[MONGO_CONFIG['collection']]
    teachers = list(collection.find({}))
    
    try:
        email_sender.connect()
        
        for teacher in teachers:
            try:
                email_sender.send_email(teacher, use_existing_connection=True)
                print(f"Email enviado a {teacher['email']}")
            except Exception as e:
                print(f"Error enviando a {teacher['email']}: {str(e)}")
    finally:
        email_sender.disconnect()

if __name__ == "__main__":
    main()