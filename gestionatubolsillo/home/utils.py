from Crypto.Cipher import AES
from django.core.files.uploadedfile import UploadedFile

from users.models import Cuenta, Cipher, EncryptedFilePDF

import base64

#Cambiar esto luego
def _encrypt_bytes(data:bytes,key:bytes,chunk_size:int=64*1024):
    #Modelo de encriptacion AES-GCM
    try:
        #Implementacion de AES 256, asegurar que clave cumple tamaño requerido 256 bits (32 Bytes)
        assert len(key) == 32
        cipher = AES.new(key=key,mode=AES.MODE_GCM)
        cipher_text_chunks = []
        for offset in range(0,len(data),chunk_size):
            chunk = data[offset:offset+chunk_size]
            cipher_text_chunks.append(cipher.encrypt(chunk))
        cipher_text = b''.join(cipher_text_chunks)

        #HMAC and cipher text returning
        tag = cipher.digest()
        nonce = cipher.nonce
        result = Cipher(HMAC=tag,Nonce=nonce,Ciphertext=cipher_text)
        return result
        
    except AssertionError:
        print('clave proporcionada no válida')
    except (ValueError, TypeError):
        print('Error cifrando bloque')


def _decrypt_bytes(payload:Cipher,key:bytes):
    try:
        #Implementacion de AES 256, asegurar que clave cumple tamaño requerido 256 bits (32 Bytes)
        assert len(key) == 32
        tag = payload.HMAC
        nonce = payload.Nonce
        ciphertext = payload.Ciphertext

        cipher = AES.new(key=key,mode=AES.MODE_GCM,nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext=ciphertext,received_mac_tag=tag)
        return plaintext

    except AssertionError:
        print('clave proporcionada no válida')
    except ValueError:
        print('Integridad comprometida')

def file_encrypt(file:UploadedFile,cuenta:Cuenta)-> Cipher:
    key = cuenta.get_key()
    file.seek(0)
    data = file.read()
    encripted_data = _encrypt_bytes(data=data,key=key)
    return encripted_data


def file_decrypt(enc_file:EncryptedFilePDF,cuenta:Cuenta):
    key = cuenta.get_key()
    enc_file.file.seek(0)
    payload = Cipher(Nonce=base64.b64decode(enc_file.nonce),
                     HMAC=base64.b64decode(enc_file.tag),
                     Ciphertext=enc_file.file.read())
    
    return _decrypt_bytes(payload=payload,key=key)