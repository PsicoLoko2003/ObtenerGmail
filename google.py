import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email import message_from_bytes

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Carga de credenciales desde un archivo JSON
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account_file.json'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('gmail', 'v1', credentials=creds)

    # Busca el mensaje con el código de verificación
    results = service.users().messages().list(userId='me', q='subject:"Your verification code"').execute()
    messages = results.get('messages', [])

    if not messages:
        return func.HttpResponse("No messages found.", status_code=200)
    
    message = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    
    # Extraer el contenido del correo
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(msg_str)

    # Busca el código en el contenido del correo
    code = extract_code_from_email(mime_msg)

    return func.HttpResponse(f"Your code is: {code}", status_code=200)

def extract_code_from_email(mime_msg):
    for part in mime_msg.walk():
        if part.get_content_type() == 'text/plain':
            body = part.get_payload(decode=True).decode()
            # Supongamos que el código está en el formato 'Código: XYZ123'
            return body.split('Código: ')[1].split()[0]
    return "Code not found"
