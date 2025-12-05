import requests
import json
from config import config

class MusicAPI:
    """音乐API工具类"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or config['default'].MUSIC_API_KEY
        # 使用网易云音乐API（示例，实际需要处理认证）
        self.search_url = 'http://musicapi.leanapp.cn/search'
        self.song_url = 'http://musicapi.leanapp.cn/song/detail'
        self.lyric_url = 'http://musicapi.leanapp.cn/lyric'
    
    def search_music(self, keywords, limit=1):
        """搜索音乐"""
        try:
            params = {
                'keywords': keywords,
                'limit': limit
            }
            response = requests.get(self.search_url, params=params)
            data = response.json()
            
            if data.get('code') == 200 and data.get('result') and data['result'].get('songs'):
                songs = data['result']['songs']
                return {
                    'success': True,
                    'songs': [
                        {
                            'id': song['id'],
                            'name': song['name'],
                            'artist': song['artists'][0]['name'],
                            'album': song['album']['name'],
                            'cover': song['album']['picUrl'] if song['album'].get('picUrl') else ''
                        } for song in songs
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': '未找到相关音乐'
                }
        except Exception as e:
            print(f"搜索音乐失败: {str(e)}")
            return {
                'success': False,
                'error': '搜索音乐时发生错误'
            }
    
    def get_song_detail(self, song_id):
        """获取歌曲详情"""
        try:
            params = {
                'ids': song_id
            }
            response = requests.get(self.song_url, params=params)
            data = response.json()
            
            if data.get('code') == 200 and data.get('songs'):
                song = data['songs'][0]
                return {
                    'success': True,
                    'song': {
                        'id': song['id'],
                        'name': song['name'],
                        'artist': song['artists'][0]['name'],
                        'album': song['album']['name'],
                        'cover': song['album']['picUrl'] if song['album'].get('picUrl') else '',
                        'duration': song['duration']  # 毫秒
                    }
                }
            else:
                return {
                    'success': False,
                    'error': '无法获取歌曲详情'
                }
        except Exception as e:
            print(f"获取歌曲详情失败: {str(e)}")
            return {
                'success': False,
                'error': '获取歌曲详情时发生错误'
            }
    
    def generate_music_card(self, song_id):
        """生成音乐卡片数据"""
        song_detail = self.get_song_detail(song_id)
        if not song_detail['success']:
            return song_detail
        
        song = song_detail['song']
        
        # 生成音乐卡片HTML结构（用于前端显示）
        card_html = f"""
        <div class="music-card" data-song-id="{song['id']}">
            <div class="music-cover">
                <img src="{song['cover']}" alt="{song['name']}" onerror="this.src='https://via.placeholder.com/150'">
                <div class="music-controls">
                    <button class="btn btn-sm btn-primary play-btn" onclick="playMusic('{song['id']}')">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary pause-btn" onclick="pauseMusic('{song['id']}')">
                        <i class="fas fa-pause"></i>
                    </button>
                    <button class="btn btn-sm btn-danger stop-btn" onclick="stopMusic('{song['id']}')">
                        <i class="fas fa-stop"></i>
                    </button>
                </div>
            </div>
            <div class="music-info">
                <h6 class="music-title">{song['name']}</h6>
                <p class="music-artist">{song['artist']}</p>
                <p class="music-album">{song['album']}</p>
            </div>
        </div>
        """
        
        return {
            'success': True,
            'card_html': card_html,
            'song': song
        }
    
    def get_music_url(self, song_id):
        """获取音乐播放URL（实际项目中可能需要特殊处理）"""
        # 注意：实际的音乐播放URL需要根据具体API获取
        # 这里使用一个模拟的URL结构
        return f"http://music.163.com/song/media/outer/url?id={song_id}.mp3"

# 测试代码
if __name__ == '__main__':
    music_api = MusicAPI()
    search_result = music_api.search_music('晴天', limit=1)
    if search_result['success']:
        song_id = search_result['songs'][0]['id']
        card_result = music_api.generate_music_card(song_id)
        print(json.dumps(card_result, ensure_ascii=False, indent=2))
