from openai import OpenAI
import requests
import urllib3
import time
import random
import json


urllib3.disable_warnings()


# get api from here https://dev.qweather.com/
weather_key = "119e208c7a5f4a60a9a1cd59728a5450"
assert len(weather_key) > 0, print("please get weather query api in https://dev.qweather.com/")


class Weather:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_location_from_api(self, location, adm=None,
                              location_range="world", lang="zh"):
        """
        Get api based on https:dev.qweather.com
        params location: the location to be queried
        params adm: superior region, for example, the superior region of Yuexiu is Guangzhou
        params location_range: query range, default global, supports cn: China, us: United States, fr: France,
        uk: United Kingdom, please check the iso-3166 standard for more information
        params lang: language, default zh, support en
        """
        url = "https://geoapi.qweather.com/v2/city/lookup?"
        params = {
            "key": self.api_key,
            "location": location,
            "range": location_range,
            "lang": lang,
        }
        if adm is not None:
            if len(adm) > 0:
                params["adm"] = adm
        session = requests.session()
        try:
            res2 = session.get(url, params=params, verify=False, timeout=15)
            if res2.status_code == 200:
                data = res2.json()
                if data.get("code", None) == '200':
                    return data.get("location", [])
                else:
                    print(data)
            else:
                print(res2)
            time.sleep(1 + random.random())
            session.close()
        except Exception as err:
            print("request error", err)
            time.sleep(3 + random.random())
            session.close()
        return []

    def get_weather_from_api(self, location: str):
        """
        Get weather information from Zefeng weather api
        :param location: location information, which can be location_id or a latitude and longitude (format: "longitude, latitude")
        """
        url = "https://devapi.qweather.com/v7/weather/3d?"
        params = {
            "location": location,
            "key": self.api_key
        }
        session = requests.session()
        try:
            res1 = session.get(url, params=params, verify=False, timeout=15)
            if res1.status_code == 200:
                data = res1.json()
                if data.get("code", "") == "200":
                    raw_data = data.get("daily", [])
                    result_data = []
                    for daily_data in raw_data:
                        result_data.append({
                            "fxDate": daily_data["fxDate"],
                            "tempMin": daily_data["tempMin"],
                            "tempMax": daily_data["tempMax"],
                            "textDay": daily_data["textDay"],
                            "textNight": daily_data["textNight"]
                        })
                    return result_data
                else:
                    print(data)
            else:
                print(res1)
            time.sleep(1 + random.random())
            session.close()
        except Exception as err:
            print("get api error，", err)
            time.sleep(3 + random.random())
            session.close()
        return []
    
def get_current_weather(location: str):
    weather = Weather(weather_key)
    location_data = weather.get_location_from_api(location)
    if len(location_data) > 0:
        location_dict = location_data[0]
        city_id = location_dict["id"]
        weather_res = weather.get_weather_from_api(city_id)
        return weather_res
    else:
        return []
    
    

if __name__ =="__main__":
    resp = get_current_weather("广州")
    print(resp)
