# 媒体库
"""
    负责扫描处理媒体库文件，缓存读写
    支持定时/手动扫描
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class MediaLibrary:
    def __init__(self, media_dir: str, cache_dir: str, scan_interval: int = 3600):
        
        self.media_dir = media_dir
        self.cache_dir = cache_dir
        self.scan_interval = scan_interval

        # 视频文件扩展名
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'}
        # 字幕文件扩展名
        self.subtitle_extensions = {'.srt', '.ass', '.ssa', '.sub', '.idx'}

        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)

    def _parse_show_info(self, filename: str) -> Optional[Dict]:
        """解析文件名中的剧集信息"""
        # 移除扩展名
        name = os.path.splitext(filename)[0]

        # 常见的季集模式
        season_patterns = [
            r'[Ss](\d{1,2})',  # S01, s01
            r'[Ss]eason\s*(\d{1,2})',  # Season 1
            r'[Ss]eason\s*(\d{1,2})',  # Season1
        ]

        # 常见的集数模式
        episode_patterns = [
            r'[Ee](\d{1,3})',  # E01, e01
            r'[Ee]pisode\s*(\d{1,3})',  # Episode 1
            r'[Ee]pisode\s*(\d{1,3})',  # Episode1
        ]

        # 尝试匹配季集和集数
        season_match = None
        episode_match = None
        season_pos = -1
        episode_pos = -1

        # 找到季集和集数的位置
        for pattern in season_patterns:
            season_match = re.search(pattern, name)
            if season_match:
                season_pos = season_match.start()
                break

        for pattern in episode_patterns:
            episode_match = re.search(pattern, name)
            if episode_match:
                episode_pos = episode_match.start()
                break

        if not season_match or not episode_match:
            return None

        season_num = int(season_match.group(1))
        episode_num = int(episode_match.group(1))

        # 提取剧名（只保留季集信息之前的部分）
        show_name = name[:season_pos].strip()

        # 清理剧名中的特殊字符
        show_name = re.sub(r'[._-]', ' ', show_name).strip()

        return {
            'show_name': show_name,
            'season_number': season_num,
            'episode_number': episode_num
        }

    def _find_subtitles(self, video_path: str) -> List[Dict]:
        """查找视频对应的字幕文件"""
        video_dir = os.path.dirname(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        subtitles = []

        # 遍历目录查找字幕文件
        for file in os.listdir(video_dir):
            if not any(file.endswith(ext) for ext in self.subtitle_extensions):
                continue

            # 检查文件名是否与视频相关
            if file.startswith(video_name):
                # 提取视频名和字幕扩展名之间的部分作为语言标识
                for ext in self.subtitle_extensions:
                    if file.endswith(ext):
                        # 移除视频名和扩展名，得到语言标识
                        language = file[len(video_name):-len(ext)]
                        if language.startswith('.'):
                            language = language[1:]  # 移除开头的点
                        subtitles.append({
                            'subtitle_file': file,
                            'language': language
                        })
                        break

        return subtitles

    def scan_media(self):
        """扫描媒体库并生成缓存"""
        library_data = {
            'library_name': os.path.basename(self.media_dir),
            'last_update': int(datetime.now().timestamp()),
            'version': '1.0',
            'shows': []
        }

        # 用于临时存储剧集信息
        shows_dict = {}

        # 遍历媒体目录
        for root, _, files in os.walk(self.media_dir):
            for file in files:
                if not any(file.endswith(ext) for ext in self.video_extensions):
                    continue

                file_path = os.path.join(root, file)
                show_info = self._parse_show_info(file)

                if not show_info:
                    continue

                show_name = show_info['show_name']
                season_num = show_info['season_number']
                episode_num = show_info['episode_number']

                # 初始化剧集数据结构
                if show_name not in shows_dict:
                    shows_dict[show_name] = {
                        'show_name': show_name,
                        'seasons': {}
                    }

                # 初始化季集数据结构
                if season_num not in shows_dict[show_name]['seasons']:
                    shows_dict[show_name]['seasons'][season_num] = {
                        'season_number': season_num,
                        'episodes': {}
                    }

                # 添加集数信息
                shows_dict[show_name]['seasons'][season_num]['episodes'][episode_num] = {
                    'episode_number': episode_num,
                    'video_file': os.path.splitext(file)[0],
                    'subtitles': self._find_subtitles(file_path)
                }

        # 转换数据结构为最终格式
        for show in shows_dict.values():
            show_data = {
                'show_name': show['show_name'],
                'seasons': []
            }

            # 对季集进行排序
            for season_num in sorted(show['seasons'].keys()):
                season = show['seasons'][season_num]
                season_data = {
                    'season_number': season['season_number'],
                    'episodes': []
                }

                # 对集数进行排序
                for episode_num in sorted(season['episodes'].keys()):
                    season_data['episodes'].append(
                        season['episodes'][episode_num])

                show_data['seasons'].append(season_data)

            library_data['shows'].append(show_data)

        # 保存缓存文件
        cache_file = os.path.join(
            self.cache_dir, 'cache_' + os.path.basename(self.media_dir) + '.json')
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(library_data, f, ensure_ascii=False, indent=2)

        return library_data
