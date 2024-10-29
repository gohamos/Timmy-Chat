import sys
import requests


def extract_googleid(url):
    id = ""
    if "google.com" in url:
        id=url.split('/')[-2]
    return id

def download_file_from_google_drive(url, destination):
    file_id=extract_googleid(url)
    print("download_file_from_google_drive() id:",file_id)
    if len(file_id)>0:
        URL = "https://drive.google.com/uc?export=download&confirm=1"
        session = requests.Session()

        response = session.get(URL, params={"id": file_id}, stream=True)
        token = get_confirm_token(response)

        if token:
            params = {"id": file_id, "confirm": token}
            response = session.get(URL, params=params, stream=True)

        save_response_content(response, destination)
        return 0;
    else:
        print("!! invalid google drive url!")
        return -1;
    


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)