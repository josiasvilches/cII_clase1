#!/usr/bin/env python3
import socket
import base64
import datetime

class SimpleSMTPClient:
    """
    Cliente SMTP básico para envío de correos electrónicos
    """
    
    def __init__(self):
        self.sock = None
        self.timeout = 30
        
    def connect(self, host, port=25):
        """
        Conecta al servidor SMTP
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        
        try:
            print(f"Conectando a {host}:{port}...")
            self.sock.connect((host, port))
            
            # Recibir saludo inicial
            response = self._recv_response()
            if not response.startswith('220'):
                raise Exception(f"Error en saludo SMTP: {response}")
            
            print(f"Servidor: {response}")
            return True
            
        except Exception as e:
            if self.sock:
                self.sock.close()
                self.sock = None
            raise e
    
    def _send_command(self, command):
        """
        Envía un comando SMTP y retorna la respuesta
        """
        if not self.sock:
            raise Exception("No conectado al servidor")
        
        print(f"Cliente: {command}")
        self.sock.send((command + '\r\n').encode('utf-8'))
        
        response = self._recv_response()
        print(f"Servidor: {response}")
        
        return response
    
    def _recv_response(self):
        """
        Recibe una respuesta del servidor SMTP
        """
        response = b''
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            response += chunk
            if response.endswith(b'\r\n'):
                break
        
        return response.decode('utf-8').strip()
    
    def helo(self, hostname='localhost'):
        """
        Envía comando HELO
        """
        response = self._send_command(f'HELO {hostname}')
        if not response.startswith('250'):
            raise Exception(f"Error en HELO: {response}")
        return True
    
    def mail_from(self, sender):
        """
        Especifica el remitente
        """
        response = self._send_command(f'MAIL FROM:<{sender}>')
        if not response.startswith('250'):
            raise Exception(f"Error en MAIL FROM: {response}")
        return True
    
    def rcpt_to(self, recipient):
        """
        Especifica un destinatario
        """
        response = self._send_command(f'RCPT TO:<{recipient}>')
        if not response.startswith('250'):
            raise Exception(f"Error en RCPT TO: {response}")
        return True
    
    def data(self, message):
        """
        Envía el mensaje
        """
        # Iniciar transmisión de datos
        response = self._send_command('DATA')
        if not response.startswith('354'):
            raise Exception(f"Error en DATA: {response}")
        
        # Enviar mensaje (terminar con línea que contiene solo un punto)
        message_lines = message.split('\n')
        for line in message_lines:
            # Escapar líneas que comienzan con punto
            if line.startswith('.'):
                line = '.' + line
            self.sock.send((line + '\r\n').encode('utf-8'))
        
        # Terminar mensaje
        response = self._send_command('.')
        if not response.startswith('250'):
            raise Exception(f"Error terminando mensaje: {response}")
        
        return True
    
    def quit(self):
        """
        Termina la sesión SMTP
        """
        if self.sock:
            try:
                self._send_command('QUIT')
            except:
                pass
            finally:
                self.sock.close()
                self.sock = None
    
    def send_email(self, smtp_server, sender, recipients, subject, body, port=25):
        """
        Envía un email completo
        """
        try:
            # Conectar
            self.connect(smtp_server, port)
            
            # Saludo
            self.helo()
            
            # Especificar remitente
            self.mail_from(sender)
            
            # Especificar destinatarios
            if isinstance(recipients, str):
                recipients = [recipients]
            
            for recipient in recipients:
                self.rcpt_to(recipient)
            
            # Construir mensaje con headers
            timestamp = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            message = f"""From: {sender}
To: {', '.join(recipients)}
Subject: {subject}
Date: {timestamp}

{body}"""
            
            # Enviar datos
            self.data(message)
            
            print("Email enviado exitosamente!")
            
        finally:
            self.quit()

def demo_smtp():
    """
    Demonstración del cliente SMTP
    """
    # Nota: Para testing real, necesitarías un servidor SMTP configurado
    # Este ejemplo muestra la estructura, pero probablemente fallará
    # sin un servidor SMTP local o configuración apropiada
    
    client = SimpleSMTPClient()
    
    try:
        client.send_email(
            smtp_server='localhost',
            sender='test@example.com',
            recipients=['recipient@example.com'],
            subject='Mensaje de prueba desde Python',
            body='Este es un mensaje de prueba enviado usando nuestro cliente SMTP personalizado.'
        )
    except Exception as e:
        print(f"Error enviando email: {e}")

if __name__ == "__main__":
    demo_smtp()