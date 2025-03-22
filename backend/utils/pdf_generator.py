from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime
import qrcode
from io import BytesIO

class PDFGenerator:
    """Clase para generar archivos PDF para la aplicación"""
    
    def __init__(self):
        """Inicializa el generador de PDF con estilos básicos"""
        self.styles = getSampleStyleSheet()
        
        # Agregar estilos personalizados
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=1,  # Centrado
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Normal_Centered',
            parent=self.styles['Normal'],
            alignment=1  # Centrado
        ))
        
        # Directorio para guardar los PDF generados
        self.output_dir = os.getenv('PDF_OUTPUT_DIR', 'static/pdfs')
        
        # Crear directorio si no existe
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_booking_pdf(self, booking):
        """
        Genera un PDF de confirmación de reserva
        
        Args:
            booking: Objeto de reserva con toda la información necesaria
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Nombre del archivo
        filename = f"booking_confirmation_{booking.booking_number}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Crear el documento
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Título del documento
        elements.append(Paragraph("CONFIRMACIÓN DE RESERVA", self.styles['Title']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Logo de la empresa (si existe)
        logo_path = 'static/images/logo.png'
        if os.path.exists(logo_path):
            img = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Información de la reserva
        elements.append(Paragraph(f"Número de Reserva: {booking.booking_number}", self.styles['Subtitle']))
        elements.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Datos del cliente
        elements.append(Paragraph("DATOS DEL CLIENTE", self.styles['Subtitle']))
        client_data = [
            ["Nombre:", booking.user.name],
            ["Email:", booking.user.email],
            ["Tipo de cliente:", booking.user.role.upper()]
        ]
        table = Table(client_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Detalles del paquete
        elements.append(Paragraph("DETALLES DEL PAQUETE", self.styles['Subtitle']))
        package_data = [
            ["Destino:", booking.package.destination],
            ["Duración:", f"{booking.package.duration} días"],
            ["Servicios incluidos:", booking.package.included_services or "No especificado"]
        ]
        table = Table(package_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Detalles de la reserva
        elements.append(Paragraph("DETALLES DE LA RESERVA", self.styles['Subtitle']))
        booking_data = [
            ["Fecha de viaje:", booking.travel_date.strftime('%d/%m/%Y')],
            ["Número de viajeros:", str(booking.number_of_travelers)],
            ["Estado:", booking.status.upper()],
            ["Solicitudes especiales:", booking.special_requests or "No hay solicitudes especiales"]
        ]
        table = Table(booking_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Detalles de pago
        elements.append(Paragraph("RESUMEN DE PAGO", self.styles['Subtitle']))
        payment_data = [
            ["Precio por persona:", f"${booking.package.price:.2f}"],
            ["Número de personas:", str(booking.number_of_travelers)],
            ["Total:", f"${booking.total_price:.2f}"]
        ]
        table = Table(payment_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Generar código QR con la información de la reserva
        qr_info = f"RESERVA:{booking.booking_number}|CLIENTE:{booking.user.name}|DESTINO:{booking.package.destination}|FECHA:{booking.travel_date}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_info)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        
        qr_img = Image(buffer, width=2*inch, height=2*inch)
        elements.append(qr_img)
        elements.append(Spacer(1, 0.2*inch))
        
        # Términos y condiciones
        elements.append(Paragraph("TÉRMINOS Y CONDICIONES", self.styles['Subtitle']))
        terms = """
        1. La reserva está sujeta a disponibilidad y confirmación.
        2. Se puede cancelar sin cargo hasta 30 días antes de la fecha de viaje.
        3. Cancelaciones con menos de 30 días de anticipación están sujetas a penalidades.
        4. Se requiere presentar identificación válida al momento del check-in.
        5. La agencia no se hace responsable por cambios en horarios de vuelo o eventos de fuerza mayor.
        """
        elements.append(Paragraph(terms, self.styles['Normal']))
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Gracias por elegir nuestra agencia de viajes", self.styles['Normal_Centered']))
        elements.append(Paragraph("Para cualquier consulta, contáctenos al +1-234-567-8900", self.styles['Normal_Centered']))
        
        # Generar el PDF
        doc.build(elements)
        
        return filepath
    
    def generate_payment_receipt(self, payment):
        """
        Genera un recibo de pago en formato PDF
        
        Args:
            payment: Objeto de pago con toda la información necesaria
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Nombre del archivo
        filename = f"payment_receipt_{payment.id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Crear el documento
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Título del documento
        elements.append(Paragraph("RECIBO DE PAGO", self.styles['Title']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Logo de la empresa (si existe)
        logo_path = 'static/images/logo.png'
        if os.path.exists(logo_path):
            img = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Información del recibo
        receipt_number = f"RCP-{payment.id}"
        elements.append(Paragraph(f"Recibo Nº: {receipt_number}", self.styles['Subtitle']))
        elements.append(Paragraph(f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Datos del cliente
        elements.append(Paragraph("DATOS DEL CLIENTE", self.styles['Subtitle']))
        client_data = [
            ["Nombre:", payment.user.name],
            ["Email:", payment.user.email]
        ]
        table = Table(client_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Detalles de la reserva
        booking = payment.booking
        elements.append(Paragraph("DETALLES DE LA RESERVA", self.styles['Subtitle']))
        booking_data = [
            ["Número de reserva:", booking.booking_number],
            ["Destino:", booking.package.destination],
            ["Fecha de viaje:", booking.travel_date.strftime('%d/%m/%Y')],
            ["Número de viajeros:", str(booking.number_of_travelers)]
        ]
        table = Table(booking_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Detalles del pago
        elements.append(Paragraph("DETALLES DEL PAGO", self.styles['Subtitle']))
        payment_data = [
            ["ID de transacción:", payment.transaction_id or "N/A"],
            ["Método de pago:", payment.payment_method],
            ["Fecha de pago:", payment.payment_date.strftime('%d/%m/%Y %H:%M')],
            ["Estado:", payment.status.upper()],
            ["Monto pagado:", f"${payment.amount:.2f}"]
        ]
        
        # Agregar últimos 4 dígitos de la tarjeta si están disponibles
        if payment.card_last_digits:
            payment_data.insert(2, ["Últimos 4 dígitos:", payment.card_last_digits])
        
        table = Table(payment_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumen de la reserva
        elements.append(Paragraph("RESUMEN FINANCIERO DE LA RESERVA", self.styles['Subtitle']))
        # Obtener el total pagado y pendiente
        from ..services.payment_service import PaymentService
        payment_service = PaymentService()
        payment_status = payment_service.check_booking_payment_status(booking.id)
        
        summary_data = [
            ["Total de la reserva:", f"${booking.total_price:.2f}"],
            ["Total pagado:", f"${payment_status['total_paid']:.2f}"],
            ["Saldo pendiente:", f"${payment_status['pending_amount']:.2f}"]
        ]
        table = Table(summary_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información adicional
        elements.append(Paragraph("INFORMACIÓN ADICIONAL", self.styles['Subtitle']))
        if payment_status['is_fully_paid']:
            elements.append(Paragraph("La reserva ha sido pagada en su totalidad.", self.styles['Normal']))
        else:
            elements.append(Paragraph(f"Aún queda un saldo pendiente de ${payment_status['pending_amount']:.2f}", self.styles['Normal']))
            elements.append(Paragraph("Por favor, complete el pago antes de la fecha de viaje.", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Aviso legal
        elements.append(Paragraph("AVISO LEGAL", self.styles['Subtitle']))
        legal_text = """
        Este recibo es un comprobante de pago oficial. Conserve este documento para cualquier consulta futura.
        Los reembolsos están sujetos a la política de cancelación aplicable a su reserva.
        Para más información, contacte a nuestro servicio de atención al cliente.
        """
        elements.append(Paragraph(legal_text, self.styles['Normal']))
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Gracias por su pago", self.styles['Normal_Centered']))
        elements.append(Paragraph("Este documento no requiere firma", self.styles['Normal_Centered']))
        
        # Generar el PDF
        doc.build(elements)
        
        return filepath
    
    def generate_itinerary_pdf(self, booking):
        """
        Genera un PDF con el itinerario detallado de un viaje
        
        Args:
            booking: Objeto de reserva con toda la información necesaria
            
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Esta función puede ser implementada según se necesite
        # con información más detallada sobre el itinerario del viaje
        pass


# Funciones de conveniencia para facilitar el uso desde otras partes de la aplicación

def generate_booking_pdf(booking):
    """Función de conveniencia para generar PDF de confirmación de reserva"""
    pdf_generator = PDFGenerator()
    return pdf_generator.generate_booking_pdf(booking)

def generate_payment_receipt(payment):
    """Función de conveniencia para generar recibo de pago"""
    pdf_generator = PDFGenerator()
    return pdf_generator.generate_payment_receipt(payment)