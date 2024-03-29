import requests
from django.core.mail import send_mail
import smtplib as smtp

from config import DevConfig


login = DevConfig.email_login
password = DevConfig.email_password

# server = smtp.SMTP('smtp.gmail.com', 587)
# server.starttls()
# server.login(login, password)

# subject = 'Theme'
# text = 'Some text'

# err = server.sendmail(login, 'vk-vk.karasev@yandex.ru',
#                       f'Subject:{subject}\n<h1>{text}</h1>')
# print(err)


YANDEX_TOKEN = 'y0_AgAAAAAJwHvOAATuwQAAAADsrZyadEkUpG9VQQuphjHUvondjmmAxS4'

headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'X-RapidAPI-Key': '396c0f4941msh224f7e17edcff9cp137bb6jsn1828d9c4e574',
    'X-RapidAPI-Host': 'text-translator2.p.rapidapi.com'
}
data = {
    'source_language': 'en',
    'target_language': 'ru',
    'text': 'What is your name?',
}

response = requests.post(
    'https://text-translator2.p.rapidapi.com/translate',
    data,
    headers=headers
)

print(response)
print(response.json())
