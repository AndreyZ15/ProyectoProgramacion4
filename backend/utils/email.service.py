import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from flask import render_template, current_app

class EmailService:
    """Servicio para enviar correos electrónicos"""
    
    def __init__(self):
        """Inicializa el servicio de correo con la configuración de la aplicación"""
        self.server = os.getenv('MAIL_SERVER', 'smtp.example.com')
        self.port = int(os.getenv('MAIL_PORT', 587))
        self.username = os.getenv('MAIL_USERNAME', 'notificaciones@tuagenciadeviajes.com')
        self.password = os.getenv('MAIL_PASSWORD', 'tu_password_de_correo')
        self.use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
        self.default_sender = os.getenv('MAIL_DEFAULT_SENDER', 'notificaciones@tuagenciadeviajes.com')
    
    def send_email(self, to, subject, html_content, text_content=None, sender=None, attachments=None):
        """
        Envía un correo electrónico
        
        Args:
            to (str or list): Destinatario(s) del correo
            subject (str): Asunto del correo
            html_content (str): Contenido HTML del correo
            text_content (str, optional): Contenido de texto plano (alternativa al HTML)
            sender (str, optional): Remitente del correo (si es diferente al predeterminado)
            attachments (list, optional): Lista de rutas de archivos para adjuntar
            
        Returns:
            bool: True si el correo se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender or self.default_sender
            
            # Convertir destinatario a lista si es un solo correo
            if isinstance(to, str):
                to = [to]
            
            msg['To'] = ', '.join(to)
            
            # Agregar contenido de texto plano (si se proporciona)
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            
            # Agregar contenido HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Agregar archivos adjuntos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                            msg.attach(part)
            
            # Conectar al servidor SMTP
            with smtplib.SMTP(self.server, self.port) as server:
                if self.use_tls:
                    server.starttls()
                
                # Iniciar sesión
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                # Enviar correo
                server.sendmail(msg['From'], to, msg.as_string())
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_welcome_email(self, user):
        """Envía un correo de bienvenida a un nuevo usuario"""
        subject = "¡Bienvenido a Tu Agencia de Viajes!"
        html_content = render_template('emails/welcome.html', user=user)
        text_content = f"¡Hola {user.name}! Bienvenido a Tu Agencia de Viajes. Gracias por registrarte."
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_booking_confirmation(self, booking, pdf_path=None):
        """Envía una confirmación de reserva"""
        subject = f"Confirmación de Reserva #{booking.booking_number}"
        
        # Obtener datos adicionales para la plantilla
        user = booking.user
        package = booking.package
        
        html_content = render_template('emails/booking_confirmation.html', 
                                      booking=booking,
                                      user=user,
                                      package=package)
        
        text_content = (f"¡Hola {user.name}! Tu reserva #{booking.booking_number} ha sido confirmada.\n"
                       f"Destino: {package.destination}\n"
                       f"Fecha de viaje: {booking.travel_date}\n"
                       f"Total: ${booking.total_price}")
        
        attachments = [pdf_path] if pdf_path else None
        
        return self.send_email(user.email, subject, html_content, text_content, attachments=attachments)
    
    def send_payment_receipt(self, payment, pdf_path=None):
        """Envía un recibo de pago"""
        booking = payment.booking
        user = payment.user
        
        subject = f"Recibo de Pago - Reserva #{booking.booking_number}"
        
        html_content = render_template('emails/payment_receipt.html',
                                      payment=payment,
                                      booking=booking,
                                      user=user)
        
        text_content = (f"¡Hola {user.name}! Hemos recibido tu pago de ${payment.amount} "
                       f"para la reserva #{booking.booking_number}.\n"
                       f"Método de pago: {payment.payment_method}\n"
                       f"Fecha de pago: {payment.payment_date}\n"
                       f"Estado: {payment.status}")
        
        attachments = [pdf_path] if pdf_path else None
        
        return self.send_email(user.email, subject, html_content, text_content, attachments=attachments)
    
    def send_booking_reminder(self, booking):
        """Envía un recordatorio de viaje próximo"""
        user = booking.user
        package = booking.package
        
        subject = f"Recordatorio de Viaje - {package.destination}"
        
        html_content = render_template('emails/booking_reminder.html',
                                      booking=booking,
                                      user=user,
                                      package=package)
        
        text_content = (f"¡Hola {user.name}! Te recordamos que tu viaje a {package.destination} "
                       f"está programado para el {booking.travel_date}.\n"
                       f"Número de reserva: {booking.booking_number}")
        
        return self.send_email(user.email, subject, html_content, text_content)
    
    def send_vip_offer(self, user, offer_details):
        """Envía una oferta exclusiva a usuarios VIP"""
        subject = "Oferta Exclusiva para Miembros VIP"
        
        html_content = render_template('emails/vip_offer.html',
                                      user=user,
                                      offer=offer_details)
        
        text_content = (f"¡Hola {user.name}! Como miembro VIP, te ofrecemos esta oferta exclusiva: "
                       f"{offer_details['title']}.\n{offer_details['description']}")
        
        return self.send_email(user.email, subject, html_content, text_content)