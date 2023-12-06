import time
import os
import requests
import shutil

from selenium import webdriver
from tqdm import tqdm
from uuid import uuid1
import json

driver_path = "chromedriver-win32/chromedriver-win64/chromedriver-win64/chromedriver.exe"
file_path = "wine1/"
comment_file_path = "comment/"
file_origin_path = "./origin/"
wine_type = {
    1: "Red",
    2: "White",
    3: "Sparkling",
    4: "Rose",
    7: "Dessert",
    24: "Fortified",
}


def data_filter(data, price, uuid):
    result = {}
    wine = data['wine1']
    # basic info
    result['id'] = uuid
    result['id_ori'] = data['id']
    result['seo_name'] = wine['seo_name']
    result['year'] = data['year']
    # result['name'] = data['name']
    result['statistics'] = data['statistics']

    # wine_info
    wine_pick = {}
    wine_pick['id'] = wine['id']

    wine_pick['name'] = wine['name']
    wine_pick['seo_name'] = wine['seo_name']
    if wine['type_id'] not in wine_type:
        wine_pick['type'] = "Fortified"
        print(result['seo_name'])
        print(wine['type_id'])
    else:
        wine_pick['type'] = wine_type[wine['type_id']]
    wine_pick['vintage_type'] = wine['vintage_type']
    wine_pick['is_natural'] = wine['is_natural']
    wine_pick['region'] = wine['region']['seo_name']
    wine_pick['country'] = wine['region']['country']['seo_name']
    wine_pick['winery'] = wine['winery']['seo_name']
    wine_pick['structure'] = wine['taste']['structure']

    result['wine1'] = wine_pick
    result['url'] = "https://www.vivino.com/US-CA/en/{0}/w/{1}?year={2}&price_id={3}".format(result['seo_name'],
                                                                                             wine['id'], result['year'],
                                                                                             price['id'])

    result['price'] = price['amount']
    return result


def get_wine(low, high, limit=1000):
    url = "https://www.vivino.com/webapi/explore/explore"
    params = {
        'country_code': 'US',
        'currency_code': 'USD',
        'grape_filter': 'varietal',
        'min_rating': '1',
        'order_by': 'best_picks',
        'order': 'desc',
        'price_range_max': str(high),
        'price_range_min': str(low),
        'page': '1',
        'language': 'en'
    }
    result = []
    page = 1
    while len(result) < limit:
        time.sleep(2)
        params['page'] = str(page)
        page += 1
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            limit = min(limit, data['explore_vintage']['records_matched'])
            records = data['explore_vintage']['records']  # 获取响应的 JSON 数据
            result.extend(records)
            # 在这里处理获取到的数据
            print(str(len(result)) + "/" + str(limit))  # 示例：打印获取到的数据
        else:
            print("请求失败，状态码:", response.status_code)
    return result


def create_base(elements: list, delete=False, origin=False):
    if delete and os.path.exists(file_path):
        shutil.rmtree(file_path)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    if delete and os.path.exists(file_origin_path):
        shutil.rmtree(file_origin_path)
    if not os.path.exists(file_origin_path):
        os.mkdir(file_origin_path)

    time.sleep(2)
    for element in tqdm(elements):
        uuid = uuid1()
        try:
            parsed_data = data_filter(element['vintage'], element['price'], str(uuid))
        except Exception as e:
            print(element['vintage']['name'])
            with open("fail.txt", "a") as f:
                f.write(element['vintage']['name'] + "\n")
            continue
        with open(file_path + str(uuid) + ".json", "w") as f:
            json.dump(parsed_data, f)
        if origin:
            with open(file_origin_path + str(uuid) + ".json", "w") as f:
                json.dump(element, f)


def load_file(string, dir = file_path):
    with open(dir + string, 'r') as json_file:
        loaded_data = json.load(json_file)
    return loaded_data


def get_comment(product, per_num=100, total=None):
    url = "https://www.vivino.com/api/wines/{0}/reviews?per_page={1}&page={2}&year=2021&language=en"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0, Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    cookies = {
        "first_time_visit": "1OXoyU41rhOpYuYmskS2SkrorBK2L6Dbxe45T24P%2BO2ObmVKUxKiobJS%2FQgmCFwSXU3cgDvW9lDHU9ooJnJ2zRP2HL6OKeubxP1GoQFHUnRqcprdrjsN%2BfGm1N1XznM383A%3D--aIHw%2Bsi9SS7S2lMV--NgMgO%2FfXOqQlTS%2Fbfl%2Bwfg%3D%3D",
        "anonymous_tracking_id": "4xi82mZw9sq%2FsHbEm%2FtPJj15UW7xvPmWWZBDzG8cfoi2%2FRziVJhTnl1gUUhhls7V983fU2%2B3nD1aedyCOL8n5%2Fw1%2BWXC7NwdD6GEW6yn5zt8nfr7gIru4yK0jQ9TNkuwoDrt9rhnh%2FzAZGrnEF%2FKMq%2BqmpaGlRYkmhBMK08UqzpQwQ75JNThZiBlHytwpQwHu%2FPK--DXPj2aB54eLgrtjJ--GU9K0fEWCZKiyga2uQ0X9A%3D%3D",
        "mp_bee7544764ece4336acb3b402265c80c_mixpanel": "%7B%22distinct_id%22%3A%20%22%24device%3A18c190486673dc-036c7035505fb9-26031051-190140-18c190486673dc%22%2C%22%24device_id%22%3A%20%2218c190486673dc-036c7035505fb9-26031051-190140-18c190486673dc%22%2C%22%24search_engine%22%3A%20%22google%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24initial_referring_domain%22%3A%20%22www.google.com%22%7D",
        "_gcl_au": "1.1.625649251.1701226776",
        "_ga": "GA1.2.406810329.1701226776",
        "__attentive_id": "b8c71251d7254bb68d0acb6eae5d0278",
        "_attn_": "eyJ1Ijoie1wiY29cIjoxNzAxMjI2Nzc2NzMwLFwidW9cIjoxNzAxMjI2Nzc2NzMwLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImI4YzcxMjUxZDcyNTRiYjY4ZDBhY2I2ZWFlNWQwMjc4XCJ9In0=",
        "__attentive_cco": "1701226776772",
        "_fbp": "fb.1.1701226777138.677796121",
        "_pin_unauth": "dWlkPVpHWTRNVEUwTURJdE0yWmhOQzAwTVRRNExXSTNPVEV0Tm1WbU9UQTFNRGt6TkRCbA",
        "_hjSessionUser_1506979": "eyJpZCI6IjNhOTU1NjBiLTM0MDEtNTA0Ny04ZjkxLTI2ODAwMGY5MWZhOSIsImNyZWF0ZWQiOjE3MDEyMjY3NzYzODEsImV4aXN0aW5nIjp0cnVlfQ==",
        "client_cache_key": "99itiKFQH%2FFBX8NC55gWXe2%2B9iBC2zS%2FEwzEsHXCUqaOANbuPlkMB%2BEZTT7we0RW9%2BrTcUhD7BPHQkxQB2Cg3JwXx%2Bg5hVUx5eHpqTNDEAQdQ7sssTH4%2FsJzccFxhM%2BPCqW2T3VUwOMSX8NwI%2BSTpTzx--fEVUwEfWCnKqZdXz--tNlx08GJzkQ90JtYI80EhQ%3D%3D",
        "eeny_meeny_personalized_upsell_module_v2": "JF0DHt8JEzL%2FsvVK%2FMX%2FHWgAK%2Fy2uDsKQxWRpxVNnrooMUCbHOi03bySmYqatKdETQZpYtFDcIEzaSFCGX%2B0%2BA%3D%3D",
        "_gid": "GA1.2.1808546375.1701554519",
        "_hp2_ses_props.3503103446": "%7B%22r%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22ts%22%3A1701554519114%2C%22d%22%3A%22www.vivino.com%22%2C%22h%22%3A%22%2FUS-CA%2Fen%2F%22%7D",
        "__attentive_ss_referrer": "https://www.google.com/, __gads:ID=6a305ef0d9a6eb74:T=1701226803:RT=1701554521:S=ALNI_MYUQw9baEhGjSUT9-VD4PjwrlKKSA",
        "__gpi": "UID=00000d0e7cb024a4:T=1701226803:RT=1701554521:S=ALNI_MakuxETwk4IDzWewWuB2gzia-HJ4Q",
        "__attentive_dv": "1",
        "recently_viewed": "s22VD3fyFNNCbN5EcEafv7usQnqbw99Io20UWE6%2BuQgesUWq7EyJAFrQrM%2FXktC3qu4HWnEPmesSDGPR3MggtdWS4DpU4n6FWePpbn9GVjXieGTBvY8xIet3jyMR2XLTnfAyraYU%2BaqLnit%2F8m7Mg%2F0v4YYH3rKVEPR9EOoaWDcKwhlnOv30XPgTJYz9rYWAuAxHic%2FOVwDwf2Zn9k2idr616dqTaTpz8YK4Vr%2BEcTf1tp8JtODvQXAWdmzOcwK508zaWZWaDAZ7Z6%2FJu6c58C3S44Gz6CsAJCJb9FR7NciNwj6RdMLqTa4PBYeTq603BVAwnAG2Yv4nA67zlMw2fQbn6S4NqHiILRNgXt764QyN7A9%2Fp9pp6UwcQWMJ1WyBmH3eXasI16f%2Bp424PQfQqS9CsYUqfafi2%2Ft3vbCkjQy6BcBnLAdgxfr89Qw7z%2FOcOinsCVQOpWTY71yb3JOkbF8jbt%2B1FOaTheK3BIrZ15EgB6ghYfxBcqCOI215zsh0tBYAVzX59DeAngZi4%2FHb72Rzo1iL--TwgWRbH0m9MQx0Yk--ZgiDdL%2BbxXH%2FNuQOV6dJQw%3D%3D",
        "_hp2_id.3503103446": "%7B%22userId%22%3A%223852596561937646%22%2C%22pageviewId%22%3A%222359589480523391%22%2C%22sessionId%22%3A%225328515241192322%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D",
        "_hjIncludedInSessionSample_1506979": "0",
        "_hjSession_1506979": "eyJpZCI6IjlkZTNhNDllLTg4MDAtNGI3NC1hNjhlLTNlMGU4NjlhN2U2NSIsImNyZWF0ZWQiOjE3MDE1NTQ1Mjk1MTAsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6dHJ1ZX0=",
        "_hjAbsoluteSessionInProgress": "0",
        "_uetsid": "547becf08e6311eeaec9f7ae3f7dfc27",
        "_uetvid": "547c10408e6311ee945505b040c8d3cb",
        "__attentive_pv": "2",
        "cto_bundle": "zlyaql9aYUFMNEglMkJjdW11ZTBTSSUyQlR6YlFsYjVkeWFpJTJGR2VrN2xDdzFzMEtoa1NPcnBrdnd2bDdlbjVvWTl2cGluSW43ZEh4YmJYbFdzb25wT0lYZmxoM3BTcFFOYTFJbkI4OWlTNHBVSlA4UEVCN3ZoSHZRbVRYb0VjJTJCRWxzNnlaNlAyV1VFJTJCeWNNSW56Q0olMkJsSTNDVklxZlElM0QlM0Q",
        "FCNEC": "%5B%5B%22AKsRol_HCr4cEFqFw-uQEp5y7nt-8SpT371Isx3CBvljTCtoT2MRJoHFFctpqpY9gc8NWGSNr8fdm1czhNsTQnJYyfjwwQzAd_7wcYyaJdUrAzNWUOyxVMs_AybELd1MnE6CDeUo_OwS8GyQXNT5Vxc63-zyLmhPXw%3D%3D%22%5D%2Cnull%2C%5B%5D%5D",
        "_ga_D35SJB5ZNL": "GS1.2.1701554520.12.1.1701555236.60.0.0",
        "csrf_token": "4kSKyPZGkPCbioCm_9RUk4yZ7_L5-VJV45NZSPyvzf2yD-c8zf14YskEvYgYlctnQi-GutSxXj6Tvn2oTa-hUg",
        "_ruby-web_session": "I%2BtbtMPNbYYXxt%2B9JUsGFc9%2BE9HXKzHoc%2Fke4rGhu2enNVlUn7imrvqN0TMQPMu%2Fy4AzfP2%2F2ZzGzMUuelKKjvGAEm6UbTO%2BbEyNaJPbIBsVtCCpLLLvorpCGqsFM9EFqzPTpekH30s9TkPrjr62cWAeVt%2FFjBmxrXcXOdaAoabKHEQKVlu7AizdhX9W2mvdmv%2B1yB4mLJcWSD3ZUJFBqHDbpO14mUmdG%2F8koi4sbrwXQHfO7SiLCaYJEIbt646B16XAlcmbO3%2FbJFW4rOPhUB5Wqh%2FNPC6LYtxwlen2dHF8Z6Y%2BBmisHrLAH2ZWoU2wwDZaoePx13OyXBwEgfpTIM4cMA2tZsT2tzanqE9VRyWVmmY3jN0rkJY6u1gIOXyWqexdnixsu%2FPGMlR2SRCz6rw9cIJDpJW1zVQ0zXMht97iU3dlDayrX9U7Dtwh3gNI9P1ZWQlWRkpct9jnTzmazBCypiwP1xCrvucL1CHCfVWW%2Bc3sZJjxq2ox%2BIEMWUgKBpKqpNMoW8yfca6pGEf1cmy4VfGxfCLWF%2BC%2F01t8lyeyXl%2BLePa1l6rkTakRLj226KdTvDFRV4GK23d7W2AhfgH8C3k88kk6EdBaTec2Qjo8KqiUk0STA1yDWqVsP3WZIW201StrpJUJILsPktWS--GDBfuXDHR9UVtD17--UwhpO3E8iSgnYBY%2F6j9FZw%3D%3D"
    }
    page = 1
    result = []
    while True:
        response = requests.get(url.format(product['wine']['id'], per_num, page), headers=headers)
        if response.status_code == 200:
            data = response.json()
            records = data['reviews']  # 获取响应的 JSON 数据
            result.extend(records)
            # 在这里处理获取到的数据
            size = len(records)
            if total and total <= len(result):
                break
            if size != per_num:
                break
            page += 1
        else:
            print("request fail", response.status_code)
    return result

def parse_comment(comments, wine_id):
    parsed = []
    statistics = ""
    for record in comments:
        result = dict()
        result["id"] = record["id"]
        result["rating"] = record["rating"]
        result["note"] = record["note"].replace('\n',' ')
        result["user_id"] = record["user"]["id"]
        result["user_statistics"] = record["user"]["statistics"]
        result["activity_id"] = record["activity"]["statistics"]
        if "flavor_word_matches" not in record:
            result["flavor_word_matches"] = []
        else:
            result["flavor_word_matches"] = record["flavor_word_matches"]
        parsed.append(result)
        statistics = statistics + str(result["user_id"]) + " | " + str(wine_id) + " | " + result["note"] + "\n"
    return parsed, statistics

def write_comment_file(data, delete=False, origin=False):
    if not os.path.exists(comment_file_path):
        os.mkdir(comment_file_path)

    uuid = data["id"]
    with open(comment_file_path + str(uuid) + ".json", "w") as f:
        json.dump(data, f)


def gather():
    high = 10
    low = 0
    for i in range(0, 10):
        print(i * 10)
        data = get_wine(i * 10, i * 10 + 10, limit=1000)
        create_base(data)


if __name__ == "__main__":
    # browser = webdriver.Chrome(executable_path=driver_path, port=9515)
    read_file = []
    if os.path.exists(comment_file_path):
        read_file = os.listdir(comment_file_path)
    readed = set(read_file)
    files = os.listdir(file_path)
    for file in tqdm(files):
        if file in readed:
            continue
        try:
            data = load_file(file)
            result = get_comment(data)
            data['comment'], static = parse_comment(result, data["wine"]["id"])
            write_comment_file(data, static)
            with open("static.txt", "a", encoding="utf-8") as f:
                f.write(static)
        except Exception as e:
            with open("comment_fail.txt", "a") as f:
                f.write(file + "|" + str(e) + "\n")
