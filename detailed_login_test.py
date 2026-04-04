import requests
import json

BASE_URL = 'http://localhost:8000'

# Make a detailed request
print('Detailed login test:')
response = requests.post(
    f'{BASE_URL}/auth/login',
    data={'username': 'alice', 'password': 'alice123'}
)

print(f'Status Code: {response.status_code}')
print(f'Headers: {dict(response.headers)}')
print(f'Content-Type: {response.headers.get("content-type")}')
print(f'Response Body: {response.text}')
print(f'Response JSON: {response.json()}')

# Also try with raw bytes
print('\n\nRaw response:')
print(response.content)
