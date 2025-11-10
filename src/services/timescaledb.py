import psycopg2
from src.config.settings import TIMESCALE_CONFIG

def get_connection():
    return psycopg2.connect(
        host=TIMESCALE_CONFIG['host'],
        port=TIMESCALE_CONFIG['port'],
        user=TIMESCALE_CONFIG['user'],
        password=TIMESCALE_CONFIG['password'],
        dbname=TIMESCALE_CONFIG['db']
    )

def get_unsent_teachers(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, subject, otherSubjects, infoAboutPersonalWork, isComplexAnalysis FROM teachers WHERE wasEmailSend = FALSE")
    teachers = cur.fetchall()
    cur.close()
    return teachers

def mark_teacher_as_sent(conn, teacher_id):
    cur = conn.cursor()
    cur.execute("UPDATE teachers SET wasEmailSend = TRUE WHERE id = %s", (teacher_id,))
    conn.commit()
    cur.close()
