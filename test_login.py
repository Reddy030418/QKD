import requests

BASE_URL = 'http://localhost:8000'

# Test login
print('Testing login with alice / alice123...')
response = requests.post(
    f'{BASE_URL}/auth/login',
    data={'username': 'alice', 'password': 'alice123'}
)

print(f'Status: {response.status_code}')
print(f'Response: {response.text}')

if response.status_code == 200:
    data = response.json()
    print(f'\n✓ Login successful!')
    token = data.get('access_token')
    print(f'  Token: {token[:50]}...')
else:
    print(f'\n✗ Login failed')
