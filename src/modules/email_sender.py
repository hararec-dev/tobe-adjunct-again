import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .template_loader import TemplateLoader
from src.config.settings import EMAIL_CONFIG

class EmailSender:
    def __init__(self):
        self.smtp_config = EMAIL_CONFIG
        self.template_loader = TemplateLoader()
        self.logger = logging.getLogger(__name__)
        self.server = None
        
    def _connect_smtp(self):
        server = smtplib.SMTP_SSL(
            self.smtp_config['server'],
            self.smtp_config['port']
        )
        server.login(
            self.smtp_config['user'],
            self.smtp_config['password']
        )
        return server
    
    def connect(self):
        """Establishes a connection to the SMTP server"""
        if self.server is None:
            self.server = self._connect_smtp()
        return self.server
    
    def disconnect(self):
        """Closes the SMTP server connection if open"""
        if self.server is not None:
            self.server.quit()
            self.server = None
    
    def send_email(self, teacher_data, use_existing_connection=False):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['user']
        msg['To'] = teacher_data['email']
        
        # Carga plantilla según género
        template = self.template_loader.load_template(teacher_data['is_woman'])
        subject_template = self.template_loader.load_subject_template()
        
        # Personaliza contenido
        msg['Subject'] = subject_template.substitute(subject=teacher_data['subject'])
        body = template.substitute(
            name=teacher_data['name'],
            subject=teacher_data['subject'],
            other_subjects_formateados="\n".join([f"- {s}" for s in teacher_data['other_subjects']]),
            personal_work=teacher_data['info_about_personal_work']
        )
        msg.attach(MIMEText(body, 'plain'))
        
        if use_existing_connection and self.server is not None:
            # Use the existing connection
            self.server.send_message(msg)
        else:
            # Create a new connection for this single email
            with self._connect_smtp() as server:
                server.send_message(msg)