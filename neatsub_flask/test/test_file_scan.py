import unittest
import os
import json
import random
import sys
import shutil
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.model.mediaLibrary import MediaLibrary

# 控制是否保留测试文件
KEEP_TEST_FILES = True

class TestMediaLibraryScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """测试类初始化，创建测试目录和文件"""
        # 测试数据 - 真实美剧数据
        cls.TV_SHOWS = [
            {
                "name": "Breaking Bad",
                "seasons": 5,
                "episodes_per_season": [7, 13, 13, 13, 16],
                "naming_pattern": "Breaking.Bad.S{season:02d}E{episode:02d}.1080p.BluRay.x264"
            },
            {
                "name": "Game of Thrones",
                "seasons": 8,
                "episodes_per_season": [10, 10, 10, 10, 10, 10, 7, 6],
                "naming_pattern": "Game.of.Thrones.S{season:02d}E{episode:02d}.1080p.WEB-DL.DD5.1.H264"
            },
            {
                "name": "The Office",
                "seasons": 9,
                "episodes_per_season": [6, 22, 25, 14, 28, 26, 26, 24, 25],
                "naming_pattern": "The.Office.S{season:02d}E{episode:02d}.720p.BluRay.x264"
            },
            {
                "name": "Stranger Things",
                "seasons": 4,
                "episodes_per_season": [8, 9, 8, 9],
                "naming_pattern": "Stranger.Things.S{season:02d}E{episode:02d}.2160p.NF.WEB-DL.DDP5.1.Atmos.HDR.HEVC"
            },
            {
                "name": "The Walking Dead",
                "seasons": 11,
                "episodes_per_season": [6, 13, 16, 16, 16, 16, 16, 16, 16, 22, 24],
                "naming_pattern": "The.Walking.Dead.S{season:02d}E{episode:02d}.1080p.AMZN.WEB-DL.DDP5.1.H.264"
            },
            {
                "name": "Better Call Saul",
                "seasons": 6,
                "episodes_per_season": [10, 10, 10, 10, 10, 13],
                "naming_pattern": "Better.Call.Saul.S{season:02d}E{episode:02d}.1080p.AMZN.WEB-DL.DDP5.1.H.264"
            },
            {
                "name": "The Last of Us",
                "seasons": 1,
                "episodes_per_season": [9],
                "naming_pattern": "The.Last.of.Us.S{season:02d}E{episode:02d}.2160p.HMAX.WEB-DL.DDP5.1.Atmos.HDR.HEVC"
            },
            {
                "name": "House of the Dragon",
                "seasons": 1,
                "episodes_per_season": [10],
                "naming_pattern": "House.of.the.Dragon.S{season:02d}E{episode:02d}.2160p.HMAX.WEB-DL.DDP5.1.Atmos.HDR.HEVC"
            }
        ]
        
        cls.FOLDER_PATTERNS = [
            "{show_name}/Season {season}",
            "{show_name}/S{season:02d}",
            "{show_name}/Season {season:02d}",
            "{show_name}/S{season:02d} - Season {season}",
            "{show_name}/Season {season:02d} - {show_name}",
            "{show_name}/S{season:02d} - {show_name}"
        ]
        
        cls.VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"]
        cls.SUBTITLE_EXTENSIONS = [".srt", ".ass", ".ssa", ".sub", ".idx"]
        cls.SUBTITLE_LANGUAGES = [
            "English",
            "Chinese",
            "Chinese.GB",
            "Chinese.BIG5",
            "English.SDH",
            "Japanese",
            "Korean",
            "Spanish",
            "French",
            "German"
        ]
        
        # 创建测试目录
        cls.test_dir = Path(__file__).parent / "test_data"
        cls.media_dir = cls.test_dir / "The US tvshow"
        cls.cache_dir = cls.test_dir / "cache"
    
    def setUp(self):
        """每个测试用例开始前执行"""
        # 清理之前的测试文件
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        
        # 创建必要的目录
        self.test_dir.mkdir(exist_ok=True)
        self.media_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # 生成测试文件
        self.generate_mock_library()
        print(f"\n测试文件已生成在: {self.test_dir}")
    
    def tearDown(self):
        """每个测试用例结束后执行"""
        if not KEEP_TEST_FILES:
            shutil.rmtree(self.test_dir)
            print("\n测试文件已清理")
        else:
            print(f"\n测试文件保留在: {self.test_dir}")
    
    def create_empty_file(self, filepath):
        """创建一个空文件"""
        Path(filepath).touch()
    
    def generate_mock_library(self):
        """生成模拟媒体库"""
        # 用于生成缓存的数据结构
        library_data = {
            'library_name': 'The US tvshow',
            'last_update': int(datetime.now().timestamp()),
            'version': '1.0',
            'shows': []
        }

        # 随机选择3-5部剧集进行测试
        selected_shows = random.sample(self.TV_SHOWS, random.randint(3, 5))

        for show in selected_shows:
            show_data = {
                'show_name': show['name'],
                'seasons': []
            }
            
            # 随机选择一个文件夹结构模式
            folder_pattern = random.choice(self.FOLDER_PATTERNS)
            
            for season in range(1, show["seasons"] + 1):
                season_data = {
                    'season_number': season,
                    'episodes': []
                }
                
                # 创建季文件夹
                season_folder = self.media_dir / folder_pattern.format(
                    show_name=show["name"],
                    season=season
                )
                season_folder.mkdir(parents=True, exist_ok=True)

                # 创建剧集文件
                for episode in range(1, show["episodes_per_season"][season-1] + 1):
                    # 基础文件名（不含扩展名）
                    base_filename = show["naming_pattern"].format(
                        season=season,
                        episode=episode
                    )
                    
                    # 随机选择视频文件扩展名
                    video_ext = random.choice(self.VIDEO_EXTENSIONS)
                    video_file = season_folder / f"{base_filename}{video_ext}"
                    self.create_empty_file(video_file)
                    
                    # 生成字幕文件
                    subtitles = []
                    for lang in random.sample(self.SUBTITLE_LANGUAGES, random.randint(1, 5)):
                        subtitle_ext = random.choice(self.SUBTITLE_EXTENSIONS)
                        subtitle_file = season_folder / f"{base_filename}.{lang}{subtitle_ext}"
                        self.create_empty_file(subtitle_file)
                        subtitles.append({
                            'subtitle_file': subtitle_file.name,
                            'language': lang
                        })
                    
                    # 添加集数信息到缓存数据
                    episode_data = {
                        'episode_number': episode,
                        'video_file': base_filename,
                        'subtitles': subtitles
                    }
                    season_data['episodes'].append(episode_data)
                
                show_data['seasons'].append(season_data)
            
            library_data['shows'].append(show_data)
        
        # 保存目标缓存文件
        self.target_cache_file = self.cache_dir / "cache_The US tvshow_target.json"
        with open(self.target_cache_file, 'w', encoding='utf-8') as f:
            json.dump(library_data, f, ensure_ascii=False, indent=2)
    
    def test_media_library_scan(self):
        """测试媒体库扫描功能"""
        # 创建媒体库实例
        media_library = MediaLibrary(
            media_dir=str(self.media_dir),
            cache_dir=str(self.cache_dir)
        )
        
        # 扫描媒体库
        media_library.scan_media()
        
        # 读取生成的缓存文件
        generated_cache_file = self.cache_dir / f"cache_{self.media_dir.name}.json"
        with open(generated_cache_file, 'r', encoding='utf-8') as f:
            generated_cache = json.load(f)
        
        # 读取目标缓存文件
        with open(self.target_cache_file, 'r', encoding='utf-8') as f:
            original_cache = json.load(f)
        
        # 比较基本信息
        self.assertEqual(generated_cache['library_name'], original_cache['library_name'])
        self.assertEqual(generated_cache['version'], original_cache['version'])
        
        # 按剧集名称排序
        generated_shows = sorted(generated_cache['shows'], key=lambda x: x['show_name'])
        original_shows = sorted(original_cache['shows'], key=lambda x: x['show_name'])
        
        # 比较剧集数量
        self.assertEqual(len(generated_shows), len(original_shows))
        
        # 比较每个剧集的详细信息
        for gen_show, orig_show in zip(generated_shows, original_shows):
            self.assertEqual(gen_show['show_name'], orig_show['show_name'])
            self.assertEqual(len(gen_show['seasons']), len(orig_show['seasons']))
            
            for gen_season, orig_season in zip(gen_show['seasons'], orig_show['seasons']):
                self.assertEqual(gen_season['season_number'], orig_season['season_number'])
                self.assertEqual(len(gen_season['episodes']), len(orig_season['episodes']))
                
                for gen_ep, orig_ep in zip(gen_season['episodes'], orig_season['episodes']):
                    self.assertEqual(gen_ep['episode_number'], orig_ep['episode_number'])
                    self.assertEqual(gen_ep['video_file'], orig_ep['video_file'])
                    self.assertEqual(len(gen_ep['subtitles']), len(orig_ep['subtitles']))
                    
                    # 按语言排序字幕
                    gen_subs = sorted(gen_ep['subtitles'], key=lambda x: x['language'])
                    orig_subs = sorted(orig_ep['subtitles'], key=lambda x: x['language'])
                    
                    for gen_sub, orig_sub in zip(gen_subs, orig_subs):
                        self.assertEqual(gen_sub['language'], orig_sub['language'])
                        self.assertEqual(gen_sub['subtitle_file'], orig_sub['subtitle_file'])

if __name__ == '__main__':
    unittest.main()
