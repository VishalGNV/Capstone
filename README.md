# Secure File Vault

A secure file storage application with AES encryption and optional face authentication built with Django.

## Features

- Secure file upload and storage with AES encryption
- Password-based authentication
- Optional face recognition authentication
- Modern and responsive UI
- File download with on-the-fly decryption
- Secure password hashing and CSRF protection

## Tech Stack

- Backend: Python (Django)
- Encryption: cryptography library (AES)
- Frontend: HTML/CSS/Bootstrap
- Authentication: Password-based + optional face recognition
- Database: SQLite (default)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your secret key and other settings
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Security Notes

- All files are encrypted using AES-256 before storage
- Passwords are securely hashed using Django's authentication system
- CSRF protection is enabled
- Face authentication is optional and uses the face_recognition library

## License

MIT License 