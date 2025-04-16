import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from .template_loader import TemplateLoader
from src.config.settings import EMAIL_CONFIG

class EmailSender:
    def __init__(self) -> None:
        self.smtp_config: Dict = EMAIL_CONFIG
        self.template_loader: TemplateLoader = TemplateLoader()
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.server: Optional[smtplib.SMTP_SSL] = None
        
    def _connect_smtp(self) -> smtplib.SMTP_SSL:
        """Creates and returns a new SMTP SSL connection"""
        server = smtplib.SMTP_SSL(
            self.smtp_config['server'],
            self.smtp_config['port']
        )
        server.login(
            self.smtp_config['user'],
            self.smtp_config['password']
        )
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

    @staticmethod
    def has_more_than_one_subject(subject_string: str) -> bool:
        """Checks if the subject string contains more than one subject"""
        if not subject_string:
            return False
        subject_names = [name.strip() for name in subject_string.split(',') if name.strip()]
        return len(subject_names) > 1

    def _create_email_message(self, teacher_data: Dict) -> MIMEMultipart:
        """Creates and returns an email message with the appropriate content"""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['user']
        msg['To'] = teacher_data['email']
        
        template = self.template_loader.load_template()
        subject_template = self.template_loader.load_subject_template()
        
        msg['Subject'] = subject_template.substitute(subject=teacher_data['subject'])
        
        have_personal_work = bool(teacher_data['infoAboutPersonalWork'])
        is_complex_analysis = bool(teacher_data['isComplexAnalysis'])
        have_many_jobs = self.has_more_than_one_subject(teacher_data['infoAboutPersonalWork'])
        
        body = template.substitute(
            name=teacher_data['name'],
            subject=teacher_data['subject'],
            other_subjects_formateados="\n".join([f"- {s}" for s in teacher_data['otherSubjects']]),
            personal_work=self._format_personal_work(teacher_data['infoAboutPersonalWork'], have_many_jobs) if have_personal_work else '',
            and_letter_c=' y c' if have_personal_work else 'C',
            complex_analysis="También tuve la oportunidad de dar una charla llamada 'Sobre la Hipótesis de Riemann' en el Coloquio de Orientación Matemática, y tengo" if is_complex_analysis else 'Tengo',
        )
        msg.attach(MIMEText(body, 'plain'))
        return msg

    @staticmethod
    def _format_personal_work(info: str, have_many_jobs: bool) -> str:
        """Formats the personal work information string"""
        return f'Su{"s" if have_many_jobs else ""} área{"s" if have_many_jobs else ""} de especialización en {info} {"son" if have_many_jobs else "es"} de mi interés'

    def send_email(self, teacher_data: Dict, use_existing_connection: bool = False) -> None:
        """Sends an email to the specified teacher"""
        msg = self._create_email_message(teacher_data)
        
        if use_existing_connection and self.server is not None:
            self.server.send_message(msg)
        else:
            with self._connect_smtp() as server:
                server.send_message(msg)