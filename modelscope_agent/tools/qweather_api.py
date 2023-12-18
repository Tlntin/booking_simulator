import requests
import urllib3
import time
import random


urllib3.disable_warnings()


# get api from here https://dev.qweather.com/
# weather_key = ""


class Weather:
    def __init__(self, api_key_free: str, api_key_pro=None):
        self.api_key_free = api_key_free
        assert len(api_key_free) > 0, print(
            "please get weather query api in https://dev.qweather.com/"
        )
        self.api_key_pro = api_key_pro

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
            "key": self.api_key_free,
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

    def get_weather_from_api(self, location: str, duration: str = "7d"):
        """
        Get weather information from HeFeng weather api
        :param location: location information, which can be location_id or a latitude and longitude (format: "longitude, latitude")
        """
        assert duration in ["7d", "15d"]
        # for free api
        if duration == "7d":
            url = "https://devapi.qweather.com/v7/weather/7d?"
            api_key = self.api_key_free
        else:
            # for standard api
            url = "https://api.qweather.com/v7/weather/15d?"
            api_key = self.api_key_pro
            assert api_key is not None, print(
                "only pro api can support weather check in 15 day's"
            )
        params = {
            "location": location,
            "key": api_key
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
                        if daily_data["textDay"] == daily_data["textNight"]:
                            weather_description = daily_data["textDay"]
                        else:
                            weather_description = daily_data["textDay"] + "转" \
                                                  + daily_data["textNight"]
                        result_data.append({
                            "date": daily_data["fxDate"],
                            "temperature_min": daily_data["tempMin"],
                            "temperature_max": daily_data["tempMax"],
                            "weather_description": weather_description
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


if __name__ == "__main__":
    weather_free_key = ""
    weather_pro_key = None


    def get_current_weather(location: str):
        weather = Weather(weather_free_key, weather_pro_key)
        location_data = weather.get_location_from_api(location)
        if len(location_data) > 0:
            location_dict = location_data[0]
            city_id = location_dict["id"]
            weather_res = weather.get_weather_from_api(city_id)
            return weather_res
        else:
            return []


    resp = get_current_weather("广州")
    print(resp)
