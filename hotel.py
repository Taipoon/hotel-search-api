import os
import re
from datetime import datetime, timedelta

import googlemaps
import requests


GOOGLE_MAP_API_KEY = os.environ['GOOGLE_MAP_API_KEY']

RAKUTEN_APPLICATION_ID = os.environ['RAKUTEN_APPLICATION_ID']
RAKUTEN_HOTEL_API_URL = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?"

gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)


class PlaceIsNotSetError(Exception):
    pass


def extract_words(string: str):
    place_search = re.search(r'「(.+?)」', string)
    time_search = re.search('\d{4}/\d{1,2}/\d{1,2}', string)
    period_search = re.search('\D(\d{1,2})泊', string)

    error_msg = []
    if place_search is None:
        error_msg.append('場所が入力されていません。「新潟駅」のように場所を指定してください。')
    if time_search is None:
        error_msg.append('チェックイン日が入力されていません。YYYY/mm/ddの形式で入力してください。')
    if period_search is None:
        error_msg.append('宿泊日数が入力されていません。02泊のように泊をつけて、半角数字2桁で入力してください。')

    if error_msg:
        error_text = '\n\n'.join(error_msg)
        return error_text

    place = place_search.group(1)
    time = time_search.group()
    period = int(period_search.group(1))

    check_in = datetime.strptime(time, '%Y/%m/%d')
    check_out = check_in + timedelta(days=period)
    check_in = check_in.strftime('%Y-%m-%d')
    check_out = check_out.strftime('%Y-%m-%d')

    result = {
        'place': place,
        'check_in': check_in,
        'check_out': check_out,
    }

    return result


def geocoding(place: str):
    if place is None or place == "":
        raise PlaceIsNotSetError

    result = gmaps.geocode(place)
    lat = result[0]["geometry"]["location"]["lat"]
    lng = result[0]["geometry"]["location"]["lng"]

    return lat, lng


def hotel_search(place, check_in, check_out, hits=5):
    latitude, longitude = geocoding(place)

    params = {
        # Application ID
        'applicationId': str(RAKUTEN_APPLICATION_ID),
        # Version
        'formatVersion': '2',
        # チェックイン日時
        'checkinDate': check_in,
        # チェックアウト日時
        'checkoutDate': check_out,
        # 緯度
        'latitude': latitude,
        # 経度
        'longitude': longitude,
        # 検索半径[km]
        'searchRadius': '3',
        'datumType': '1',
        'hits': hits,
        }
    try:
        response = requests.get(RAKUTEN_HOTEL_API_URL, params=params)
        content = response.json()
        # Error
        error = content.get("error")
        if error is not None:
            msg = content["error_description"]
            return msg

        from pprint import pprint

        # 全ホテル情報
        hotels = content['hotels']
        # 検索結果情報
        paging_info = content['pagingInfo']
        # 結果
        result = '▼▼▼検索結果▼▼▼'
        for hotel_data in hotels:
            hotel_basic_info = hotel_data[0]['hotelBasicInfo']
            hotel_rating_info = hotel_data[1]['hotelRatingInfo']

            # ホテルの属性
            hotel_name = hotel_basic_info['hotelName']
            hotel_kana_name = hotel_basic_info['hotelKanaName']
            hotel_special = hotel_basic_info['hotelSpecial']
            nearest_station = hotel_basic_info['nearestStation']
            postal_code = hotel_basic_info['postalCode']
            prefecture = hotel_basic_info['address1']
            city = hotel_basic_info['address2']
            access = hotel_basic_info['access']
            review_average = hotel_basic_info['reviewAverage']
            telephone_no = hotel_basic_info['telephoneNo']
            hotel_information_url = hotel_basic_info['hotelInformationUrl']

            # レスポンス情報
            first = paging_info['first']
            last = paging_info['last']
            record_count = paging_info['recordCount']
            page_count = paging_info['pageCount']
            page = paging_info['page']

            print('ホテル名　　:', hotel_name, f'({hotel_kana_name})')
            print('評価　　　　:　★', review_average)
            print('ホテルの説明:', hotel_special)
            print('住所　　　　:', '〒', postal_code, prefecture, city)
            print('アクセス　　:', access)
            print('電話番号　　:', telephone_no)
            print('最寄り駅　　:', nearest_station)
            print('URL 　　　 :', hotel_information_url)
            print('------------------------------------------------')

            result += f"""\
■ ホテル名
{hotel_name}({hotel_kana_name})

■ 住所
〒{postal_code}
{prefecture} {city}

■ アクセス
最寄り駅：{nearest_station}
{access}

■ URL
{hotel_information_url}\


"""
        result += f"""\
\n
「{place}」の周辺3km圏内に、全{record_count}件のホテルが見つかりました。\n
そのうち、{last}件を表示しています。\
"""
        return result

    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        return "API接続中に何らかのエラーが発生しました"


if __name__ == '__main__':

    text = input()
    r = extract_words(text)
    print(r)
    hotel_search(r['place'], r['check_in'], r['check_out'])