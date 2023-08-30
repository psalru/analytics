import requests


def get_data_by_url(url: str) -> list:
    resp = requests.get(url)
    result = []

    if resp.status_code == 200:
        json_data = resp.json()
        result += json_data['results']
        next_url = json_data['next']

        if next_url:
            result += get_data_by_url(next_url)
    else:
        print(f"{url} return status code {resp.status_code}")

    return result
