import time

from pymongo import MongoClient

from src.config.settings import MONGO_CONFIG
from src.modules.email_sender import EmailSender


def main():
    email_sender = EmailSender()
    client = MongoClient(
        host=MONGO_CONFIG["host"],
        port=MONGO_CONFIG["port"],
        username=MONGO_CONFIG["username"],
        password=MONGO_CONFIG["password"],
    )

    db = client[MONGO_CONFIG["database"]]
    collection = db[MONGO_CONFIG["collection"]]
    teachers = list(collection.find({"wasEmailSend": False}))
    start_time = time.time()

    try:
        email_sender.connect()
        sent_count = 0

        for teacher in teachers:
            try:
                email_sender.send_email(teacher, use_existing_connection=True)
                collection.update_one({"_id": teacher["_id"]}, {"$set": {"wasEmailSend": True}})
                print(f"Email enviado a {teacher['email']}")
                sent_count += 1
            except Exception as e:
                print(f"Error enviando a {teacher['email']}: {str(e)}")
    finally:
        email_sender.disconnect()
        client.close()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nSe enviaron {sent_count} emails en {execution_time:.2f} segundos")


if __name__ == "__main__":
    main()
