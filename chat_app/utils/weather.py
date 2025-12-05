import requests
import json
from config import config

class WeatherAPI:
    """天气API工具类"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or config['default'].WEATHER_API_KEY
        # 使用和风天气API（示例）
        self.base_url = 'https://devapi.qweather.com/v7/weather/now'
        self.city_url = 'https://geoapi.qweather.com/v2/city/lookup'
    
    def get_city_id(self, city_name):
        """根据城市名获取城市ID"""
        try:
            params = {
                'key': self.api_key,
                'location': city_name,
                'lang': 'zh'
            }
            response = requests.get(self.city_url, params=params)
            data = response.json()
            
            if data.get('code') == '200' and data.get('location'):
                return data['location'][0]['id']
            else:
                return None
        except Exception as e:
            print(f"获取城市ID失败: {str(e)}")
            return None
    
    def get_weather(self, city_name):
        """获取指定城市的天气信息"""
        # 获取城市ID
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {
                'success': False,
                'error': '无法获取城市信息'
            }
        
        try:
            params = {
                'key': self.api_key,
                'location': city_id,
                'lang': 'zh'
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data.get('code') == '200' and data.get('now'):
                now = data['now']
                return {
                    'success': True,
                    'city': city_name,
                    'temperature': now['temp'],
                    'description': now['text'],
                    'humidity': now['humidity'],
                    'wind_speed': now['windSpeed'],
                    'type': self._get_weather_type(now['text'])  # 获取天气类型用于背景切换
                }
            else:
                return {
                    'success': False,
                    'error': '无法获取天气信息'
                }
        except Exception as e:
            print(f"获取天气失败: {str(e)}")
            return {
                'success': False,
                'error': '获取天气信息时发生错误'
            }
    
    def _get_weather_type(self, description):
        """根据天气描述获取天气类型（用于背景切换）"""
        description = description.lower()
        
        if '雨' in description:
            return 'rain'
        elif '雪' in description:
            return 'snow'
        elif '晴' in description:
            return 'sunny'
        elif '云' in description or '阴' in description:
            return 'cloudy'
        elif '雾' in description or '霾' in description:
            return 'fog'
        else:
            return 'default'

# 测试代码
if __name__ == '__main__':
    weather_api = WeatherAPI()
    result = weather_api.get_weather('北京')
    print(json.dumps(result, ensure_ascii=False, indent=2))
