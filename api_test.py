import requests

def test_get_csv_files(company_id):
    url = f'http://127.0.0.1:8000/company/{company_id}/csvfiles/'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # 'data' variable now contains the response data
        print(data)
    else:
        print('Error:', response.status_code)

# Replace 'company_id' with the actual ID of the company you want to retrieve CSV files for
test_get_csv_files(1)
