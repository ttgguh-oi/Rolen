import requests
import json
from config import config

class NewsAPI:
    """新闻API工具类"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or config['default'].NEWS_API_KEY
        # 使用聚合数据新闻API（示例）
        self.base_url = 'http://v.juhe.cn/toutiao/index'
    
    def get_60s_news(self):
        """获取每日60秒新闻（示例实现）"""
        try:
            params = {
                'key': self.api_key,
                'type': 'top',  # 获取头条新闻
                'page': 1,
                'page_size': 5  # 获取5条新闻，模拟60秒新闻
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data.get('error_code') == 0 and data.get('result') and data['result'].get('data'):
                news_list = data['result']['data']
                return {
                    'success': True,
                    'news': [
                        {
                            'title': news['title'],
                            'content': news['author_name'] + ' - ' + news['date'],
                            'url': news['url']
                        } for news in news_list[:5]  # 取前5条新闻
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': '无法获取新闻信息'
                }
        except Exception as e:
            print(f"获取新闻失败: {str(e)}")
            return {
                'success': False,
                'error': '获取新闻信息时发生错误'
            }
    
    def get_custom_news(self, keywords=None, category=None):
        """获取自定义新闻"""
        try:
            params = {
                'key': self.api_key,
                'type': category or 'top',
                'page': 1,
                'page_size': 5
            }
            
            if keywords:
                params['keyword'] = keywords
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data.get('error_code') == 0 and data.get('result') and data['result'].get('data'):
                news_list = data['result']['data']
                return {
                    'success': True,
                    'news': [
                        {
                            'title': news['title'],
                            'content': news['author_name'] + ' - ' + news['date'],
                            'url': news['url']
                        } for news in news_list[:5]
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': '无法获取新闻信息'
                }
        except Exception as e:
            print(f"获取新闻失败: {str(e)}")
            return {
                'success': False,
                'error': '获取新闻信息时发生错误'
            }

# 测试代码
if __name__ == '__main__':
    news_api = NewsAPI()
    result = news_api.get_60s_news()
    print(json.dumps(result, ensure_ascii=False, indent=2))
