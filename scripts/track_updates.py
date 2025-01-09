import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
import re

def load_config():
    config_path = Path(__file__).parent.parent / "json" / "track_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def download_and_extract_zip(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            return None
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "module.zip"
            # 下载zip文件
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            try:
                # 解压文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                print(f"Error: Invalid zip file from {url}")
                return None
            except NotImplementedError as e:
                print(f"Error downloading/extracting zip: {e}")
                return None
            
            # 获取所有文件名
            files = []
            for root, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    files.append(filename.lower())
            return files
    except Exception as e:
        print(f"Error downloading/extracting zip: {e}")
        return None

def get_antifeatures_from_files(files):
    """
    根据MMRL定义的antifeatures进行检测
    """
    antifeatures = []
    
    # 检查广告相关文件
    ad_patterns = [r'\bad[s]?\b', r'\badvertis(ing|ement)\b', r'广告']
    if any(any(re.search(pattern, f, re.I) for pattern in ad_patterns) for f in files):
        antifeatures.append('ads')
    
    # 检查追踪相关文件
    track_patterns = [r'\btrack(er|ing)?\b', r'\banalytics?\b', r'\bstatistics?\b', r'\btelemetry\b']
    if any(any(re.search(pattern, f, re.I) for pattern in track_patterns) for f in files):
        antifeatures.append('tracking')
    
    # 检查非自由网络服务
    net_patterns = [
        r'\b(google|facebook|amazon|azure|aws)[-_]?(api|sdk|service)\b',
        r'\bcloud[-_]?(api|service)\b'
    ]
    if any(any(re.search(pattern, f, re.I) for pattern in net_patterns) for f in files):
        antifeatures.append('nonfreenet')
    
    # 检查非自由资产
    asset_patterns = ['.mp3', '.aac', '.wma', '.m4p', '.m4v', 'proprietary', 'nonfree']
    if any(f.lower().endswith(tuple(asset_patterns)) or any(p in f.lower() for p in asset_patterns) for f in files):
        antifeatures.append('nonfreeassets')
    
    # 检查非自由依赖
    dep_patterns = [r'nonfree[-_]?dep', r'proprietary[-_]?dep']
    if any(any(re.search(pattern, f, re.I) for pattern in dep_patterns) for f in files):
        antifeatures.append('nonfreedep')
    
    # 检查非自由附加组件
    addon_patterns = [r'nonfree[-_]?addon', r'premium[-_]?feature']
    if any(any(re.search(pattern, f, re.I) for pattern in addon_patterns) for f in files):
        antifeatures.append('nonfreeadd')
    
    # 检查NSFW内容
    nsfw_patterns = [r'\bnsfw\b', r'\badult\b', r'\bmature\b']
    if any(any(re.search(pattern, f, re.I) for pattern in nsfw_patterns) for f in files):
        antifeatures.append('nsfw')
    
    return antifeatures

def get_github_repo_info(repo_url):
    # 检查是否是GitHub URL
    if not repo_url.startswith('https://github.com/'):
        return {
            'license': '',
            'antifeatures': [],
            'updated_at': ''
        }
    
    # 从URL中提取owner和repo名称
    match = re.match(r'https://github.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        return {
            'license': '',
            'antifeatures': [],
            'updated_at': ''
        }
    
    owner, repo = match.groups()
    headers = {}
    if 'GITHUB_TOKEN' in os.environ:
        headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
    
    # 获取仓库信息
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return {
                'license': '',
                'antifeatures': [],
                'updated_at': ''
            }
        
        repo_info = response.json()
        
        # 检查仓库状态
        antifeatures = []
        
        # 检查源代码可用性
        if repo_info.get('archived', False) or repo_info.get('disabled', False):
            antifeatures.append('nosourcesince')
        
        # 检查是否是私有仓库或闭源
        if repo_info.get('private', False) or not repo_info.get('license'):
            antifeatures.append('upstreamnonfree')
        
        # 检查已知漏洞
        try:
            vuln_url = f'https://api.github.com/repos/{owner}/{repo}/security/advisories'
            response = requests.get(vuln_url, headers=headers)
            if response.status_code == 200 and response.json():
                antifeatures.append('knownvuln')
        except:
            pass
        
        # 检查上游依赖
        dependencies_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
        try:
            response = requests.get(dependencies_url, headers=headers)
            if response.status_code == 200:
                files = [f['name'].lower() for f in response.json()]
                antifeatures.extend(get_antifeatures_from_files(files))
        except:
            pass
        
        return {
            'license': repo_info.get('license', {}).get('spdx_id', ''),
            'antifeatures': list(set(antifeatures)),  # 去重
            'updated_at': repo_info.get('updated_at', '')
        }
    except:
        return {
            'license': '',
            'antifeatures': [],
            'updated_at': ''
        }

def get_module_categories(files):
    categories = []
    
    # Zygisk模块
    zygisk_patterns = [r'zygisk', r'zygote', r'riru']
    if any(any(pattern in f.lower() for pattern in zygisk_patterns) for f in files):
        categories.append('Zygisk')
    
    # 脚本模块
    script_files = ['service.sh', 'post-fs-data.sh', 'customize.sh', 'install.sh']
    if any(f.lower() in [sf.lower() for sf in script_files] for f in files):
        categories.append('Script')
    
    # 系统模块
    system_patterns = [r'system', r'system\.prop', r'vendor', r'product', r'boot', r'recovery']
    if any(any(pattern in f.lower() for pattern in system_patterns) for f in files):
        categories.append('System')
    
    # 主题模块
    theme_patterns = [r'theme', r'style', r'overlay', r'skin', r'color', r'appearance', r'icon', r'ui', r'interface']
    if any(any(pattern in f.lower() for pattern in theme_patterns) for f in files):
        categories.append('Theme')
    
    # 字体模块
    font_patterns = [r'font', r'typeface', r'\.ttf$', r'\.otf$', r'\.woff2?$', r'emoji']
    if any(any(re.search(pattern, f.lower()) for pattern in font_patterns) for f in files):
        categories.append('Font')
    
    # 音频模块
    audio_patterns = [r'audio', r'sound', r'music', r'ringtone', r'\.wav$', r'\.mp3$', r'\.m4a$', r'\.ogg$', r'dolby', r'equalizer', r'speaker']
    if any(any(re.search(pattern, f.lower()) for pattern in audio_patterns) for f in files):
        categories.append('Audio')
    
    # 框架模块
    framework_patterns = [r'framework', r'xposed', r'lsposed', r'edxposed', r'taichi', r'hook', r'inject']
    if any(any(pattern in f.lower() for pattern in framework_patterns) for f in files):
        categories.append('Framework')
    
    # 安全模块
    security_patterns = [r'security', r'privacy', r'protect', r'safe', r'crypto', r'permission', r'lock', r'hide', r'mask']
    if any(any(pattern in f.lower() for pattern in security_patterns) for f in files):
        categories.append('Security')
    
    # 网络模块
    network_patterns = [r'network', r'wifi', r'proxy', r'vpn', r'dns', r'hosts', r'firewall', r'internet', r'data', r'5g', r'4g']
    if any(any(pattern in f.lower() for pattern in network_patterns) for f in files):
        categories.append('Network')
    
    # 性能模块
    perf_patterns = [r'performance', r'boost', r'tweak', r'optimize', r'governor', r'kernel', r'cpu', r'gpu', r'ram', r'memory', r'battery']
    if any(any(pattern in f.lower() for pattern in perf_patterns) for f in files):
        categories.append('Performance')
    
    # 实用工具
    util_patterns = [r'util', r'tool', r'helper', r'manager', r'settings?', r'config', r'backup', r'restore', r'clean']
    if any(any(pattern in f.lower() for pattern in util_patterns) for f in files):
        categories.append('Utility')

    # 游戏相关
    game_patterns = [r'game', r'gaming', r'fps', r'pubg', r'codm', r'unity', r'unreal']
    if any(any(pattern in f.lower() for pattern in game_patterns) for f in files):
        categories.append('Gaming')

    # 相机相关
    camera_patterns = [r'camera', r'photo', r'video', r'gcam', r'lens']
    if any(any(pattern in f.lower() for pattern in camera_patterns) for f in files):
        categories.append('Camera')

    # 调试工具
    debug_patterns = [r'debug', r'log', r'trace', r'test', r'monitor', r'analyze']
    if any(any(pattern in f.lower() for pattern in debug_patterns) for f in files):
        categories.append('Debug')

    # 多媒体
    media_patterns = [r'media', r'player', r'codec', r'stream', r'record']
    if any(any(pattern in f.lower() for pattern in media_patterns) for f in files):
        categories.append('Multimedia')
    
    # 去重并返回
    return list(set(categories))

def create_track_json(repo_info):
    # 获取GitHub仓库信息
    github_info = get_github_repo_info(repo_info["url"])
    if not github_info:
        return None

    # 获取update.json内容和模块文件内容
    try:
        response = requests.get(repo_info["update_to"])
        if response.status_code == 200:
            update_json = response.json()
            if 'zipUrl' in update_json:
                # 下载并解析模块文件
                files = download_and_extract_zip(update_json['zipUrl'])
                if files:
                    categories = get_module_categories(files)
                    # 从zip文件内容检测antifeatures
                    zip_antifeatures = get_antifeatures_from_files(files)
                else:
                    categories = []
                    zip_antifeatures = []
            else:
                categories = []
                zip_antifeatures = []
        else:
            categories = []
            zip_antifeatures = []
    except Exception:
        categories = []
        zip_antifeatures = []

    # 合并所有来源的 antifeatures
    antifeatures = list(set(github_info['antifeatures'] + zip_antifeatures))

    # 生成readme链接
    if repo_info["url"].startswith('https://github.com/'):
        readme_url = f"https://raw.githubusercontent.com/{repo_info['url'].split('github.com/')[1]}/main/README.md"
    else:
        readme_url = ""

    track = {
        "id": repo_info["module_id"],
        "enable": repo_info.get("enable", True),
        "verified": repo_info.get("verified", False),
        "update_to": repo_info["update_to"],
        "license": github_info["license"],
        "homepage": repo_info.get("homepage", ""),
        "source": repo_info["source"],
        "support": repo_info.get("support", ""),
        "donate": repo_info.get("donate", ""),
        "categories": categories,
        "readme": readme_url
    }
    
    # 只有当有antifeatures时才添加到track.json
    if antifeatures:
        track["antifeatures"] = antifeatures
        
    return track

def update_tracks():
    config = load_config()
    root_dir = Path(__file__).parent.parent
    
    for repo in config["repositories"]:
        module_dir = root_dir / "modules" / repo["module_id"]
        module_dir.mkdir(parents=True, exist_ok=True)
        
        track_path = module_dir / "track.json"
        track_data = create_track_json(repo)
        
        if track_data:
            with open(track_path, 'w') as f:
                json.dump(track_data, f, indent=4)
        else:
            print(f"Failed to process repository: {repo['url']}")
            
if __name__ == "__main__":
    update_tracks()
