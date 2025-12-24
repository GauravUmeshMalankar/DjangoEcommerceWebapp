# Django E-Commerce Web App 🛒

A Django-based e-commerce application with Cashfree payment gateway integration.

## Features
- Product listing
- Cart & checkout
- Cashfree payment gateway (Sandbox)
- SQLite database
- Django 5.x

## Tech Stack
- Django
- SQLite
- Cashfree PG
- HTML / CSS / Bootstrap

## Screenshots

### Home Page
![Home Page](media/uploads/demo_upload/01.png)


### Product Page
![Product Page](media/uploads/demo_upload/02.png)

### Cart Page
![Cart Page](media/uploads/demo_upload/04.png)

### Checkout Page
![Checkout Page](media/uploads/demo_upload/05.png)

### Summary Page
![Summary Page](media/uploads/demo_upload/06.png)

### Payment Page
![Payment Page](media/uploads/demo_upload/08.png)

## Setup Instructions

1. Clone repository
```bash
git clone https://github.com/GauravUmeshMalankar/DjangoEcommerceWebapp.git
Create virtual environment

2. Create Virtual Environment
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt

4. Create .env file
Put your Secret keys
DJANGO_SECRET_KEY=your-secret
CASHFREE_APP_ID=your-id
CASHFREE_SECRET_KEY=your-key

5. Run the following commands
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


