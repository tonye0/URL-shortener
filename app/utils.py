import string
import random

import qrcode
from tempfile import NamedTemporaryFile

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def generate_qr_code(url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=8,
    )
    # Add the URL to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create a temporary file to save the QR code image
    with NamedTemporaryFile(delete=False) as tmp_file:
        # Generate the QR code image
        qr.make_image().save(tmp_file.name)
        return tmp_file.name
