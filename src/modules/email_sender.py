import logging
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

from src.config.settings import EMAIL_CONFIG, PHONE_NUMBER

from .template_loader import TemplateLoader


class EmailSender:
    def __init__(self) -> None:
        self.smtp_config: Dict = EMAIL_CONFIG
        self.template_loader: TemplateLoader = TemplateLoader()
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.server: Optional[smtplib.SMTP_SSL] = None
        self.phone_number: str = PHONE_NUMBER

    def _connect_smtp(self) -> smtplib.SMTP_SSL:
        """Creates and returns a new SMTP SSL connection"""
        server = smtplib.SMTP_SSL(self.smtp_config["server"], self.smtp_config["port"])
        server.login(self.smtp_config["user"], self.smtp_config["password"])
        return server

    def connect(self) -> smtplib.SMTP_SSL:
        """Establishes a connection to the SMTP server"""
        if self.server is None:
            self.server = self._connect_smtp()
        return self.server

    def disconnect(self) -> None:
        """Closes the SMTP server connection if open"""
        if self.server is not None:
            self.server.quit()
            self.server = None

    def _format_subjects(self, teacher_data: Dict) -> str:
        """Formatea los subjects tomando el subject principal y hasta 5 aleatorios de otherSubjects"""
        # Incluir siempre el subject principal
        all_subjects = [teacher_data["subject"]]

        # Agregar otros subjects disponibles
        other_subjects = teacher_data.get("otherSubjects", [])

        # Si hay más de 5 subjects en total, seleccionar aleatoriamente
        if len(other_subjects) > 4:  # Porque ya tenemos 1 del subject principal
            # Seleccionar 4 aleatorios de otherSubjects (para tener máximo 5 en total)
            selected_others = random.sample(other_subjects, 4)
            all_subjects.extend(selected_others)
        else:
            # Agregar todos los otherSubjects disponibles
            all_subjects.extend(other_subjects)

        # Crear string separado por comas
        return ", ".join(all_subjects)

    def _create_email_message(self, teacher_data: Dict) -> MIMEMultipart:
        """Creates and returns an email message with the appropriate content"""
        msg = MIMEMultipart()
        msg["From"] = self.smtp_config["user"]
        msg["To"] = teacher_data["email"]

        template = self.template_loader.load_template()
        subject_template = self.template_loader.load_subject_template()

        # El asunto ahora es fijo, no necesita sustitución
        msg["Subject"] = subject_template.template

        # Formatear los subjects según la nueva lógica
        subjects_str = self._format_subjects(teacher_data)

        body = template.substitute(
            name=teacher_data["name"],
            subjects=subjects_str,
            phone_number=self.phone_number,
        )
        msg.attach(MIMEText(body, "plain"))
        return msg

    def send_email(self, teacher_data: Dict, use_existing_connection: bool = False) -> None:
        """Sends an email to the specified teacher"""
        msg = self._create_email_message(teacher_data)

        if use_existing_connection and self.server is not None:
            self.server.send_message(msg)
        else:
            with self._connect_smtp() as server:
                server.send_message(msg)
