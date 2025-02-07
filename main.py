import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import argparse


def shorten_link(access_token, url_to_shorten):
    url = "https://api.vk.com/method/utils.getShortLink"
    params = {
        "url": url_to_shorten,
        "access_token": access_token,
        "v": "5.199"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    api_response = response.json()

    if "response" in api_response:
        return api_response["response"]["short_url"]

    raise requests.exceptions.HTTPError(api_response["error"]["error_msg"])

def get_clicks_count(access_token, short_url):
    short_url_id = short_url.split("/")[-1]

    url = "https://api.vk.com/method/utils.getLinkStats"
    params = {
        "key": short_url_id,
        "access_token": access_token,
        "interval": "month",
        "v": "5.199",
        "extended": "0",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    api_response = response.json()


    if "response" in api_response or "stats" in api_response["response"]:
        stats = api_response["response"]["stats"]
        return stats[0]["clicks"]

    raise requests.exceptions.HTTPError(api_response["error"]["error_msg"])

def is_short_link(access_token, url):
    parsed_url = urlparse(url)

    if parsed_url.netloc != "vk.cc" or not parsed_url.path:
        return False

    params = {
        "key": parsed_url.path[1:],
        "access_token": access_token,
        "v": "5.199"
    }


    response = requests.get("https://api.vk.com/method/utils.getLinkStats", params=params)
    response.raise_for_status()
    api_response = response.json()

    return "response" in api_response


def main():

    load_dotenv()
    access_token = os.environ["VK_API_KEY"]

    parser = argparse.ArgumentParser(description="Сокращение ссылок и получение статистики кликов.")
    parser.add_argument("url", help="URL для сокращения или проверки кликов")
    args = parser.parse_args()

    url_to_shorten = args.url

    try:
        if is_short_link(access_token, url_to_shorten):
            clicks_count = get_clicks_count(access_token, url_to_shorten)
            print("По вашей ссылке перешли", clicks_count, "раз")
        else:
            if urlparse(url_to_shorten).scheme in ["http", "https"]:
                short_url = shorten_link(access_token, url_to_shorten)
                print("Сокращенная ссылка:", short_url)
            else:
                print("Ошибка: Введенная ссылка некорректна.")

    except requests.exceptions.HTTPError as error:
        print("Ошибка при выполнении запроса:\n{0}".format(error))
    except requests.exceptions.RequestException:
        print("Ошибка при выполнении запроса, проверьте соединение.")
    except Exception as e:
        print("Произошла ошибка:\n{0}".format(e))


if __name__ == "__main__":
    main()
