import json
import os
import tempfile
import zipfile
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests
import re

# 定义antifeatures的标准顺序
ANTIFEATURE_ORDER = [
    'ads',
    'knownvuln',
    'nsfw',
    'nosourcesince',
    'nonfreeadd',
    'nonfreeassets',
    'nonfreedep',
    'nonfreenet',
    'tracking',
    'upstreamnonfree'
]

def load_config():
    config_path = Path(__file__).parent.parent / "json" / "track_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def download_and_extract_zip(url, cache_dir=None):
    """下载并解压zip文件，支持缓存"""
    try:
        # 创建缓存目录（如果提供了缓存目录）
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            # 生成缓存文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_path = Path(cache_dir) / f"{url_hash}.json"
            
            # 检查缓存是否存在且有效（7天内）
            if cache_path.exists():
                try:
                    with open(cache_path, 'r') as f:
                        cache_data = json.load(f)
                    
                    cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                    now = datetime.now()
                    
                    # 如果缓存在7天内，直接返回缓存数据
                    if (now - cache_time) < timedelta(days=7):
                        print(f"Using cached data for {url}")
                        return cache_data.get('files', [])
                except (json.JSONDecodeError, KeyError):
                    # 缓存文件损坏，继续下载
                    print(f"Cache file for {url} is corrupted")
                    pass
        
        # 下载文件
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print(f"Failed to download from {url}: HTTP {response.status_code}")
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
            
            # 缓存结果（如果提供了缓存目录）
            if cache_dir and files:
                try:
                    cache_data = {
                        'timestamp': datetime.now().isoformat(),
                        'files': files
                    }
                    with open(cache_path, 'w') as f:
                        json.dump(cache_data, f)
                    print(f"Cached data for {url}")
                except Exception as e:
                    print(f"Failed to cache data: {e}")
                    
            return files
    except Exception as e:
        print(f"Error downloading/extracting zip: {e}")
        return None

def get_antifeatures_from_files(files):
    """
    根据MMRL定义的antifeatures进行检测
    """
    antifeatures = []
    
    # 过滤文件列表，只保留字符串类型的项目
    valid_files = [f for f in files if isinstance(f, str)]
    
    # 检查广告相关文件 - 修复误将"去广告"识别为广告的问题
    ad_patterns = [r'\bad[s]?\b', r'\badvertis(ing|ement)\b', r'广告']
    ad_exclusion_patterns = [r'去广告', r'block[-_]?ads?', r'ad[-_]?block', r'no[-_]?ads?', r'remove[-_]?ads?']
    
    # 先检查是否是去广告类模块
    is_ad_blocker = any(any(re.search(pattern, f, re.I) for pattern in ad_exclusion_patterns) for f in valid_files)
    
    # 如果不是去广告类模块，再检查是否包含广告
    if not is_ad_blocker and any(any(re.search(pattern, f, re.I) for pattern in ad_patterns) for f in valid_files):
        antifeatures.append('ads')
    
    # 检查追踪相关文件
    track_patterns = [r'\btrack(er|ing)?\b', r'\banalytics?\b', r'\bstatistics?\b', r'\btelemetry\b']
    if any(any(re.search(pattern, f, re.I) for pattern in track_patterns) for f in valid_files):
        antifeatures.append('tracking')
    
    # 检查非自由网络服务
    net_patterns = [
        r'\b(google|facebook|amazon|azure|aws)[-_]?(api|sdk|service)\b',
        r'\bcloud[-_]?(api|service)\b'
    ]
    if any(any(re.search(pattern, f, re.I) for pattern in net_patterns) for f in valid_files):
        antifeatures.append('nonfreenet')
    
    # 检查非自由资产
    asset_patterns = ['.mp3', '.aac', '.wma', '.m4p', '.m4v', 'proprietary', 'nonfree']
    if any(f.lower().endswith(tuple(asset_patterns)) or any(p in f.lower() for p in asset_patterns) for f in valid_files):
        antifeatures.append('nonfreeassets')
    
    # 检查非自由依赖
    dep_patterns = [r'nonfree[-_]?dep', r'proprietary[-_]?dep']
    if any(any(re.search(pattern, f, re.I) for pattern in dep_patterns) for f in valid_files):
        antifeatures.append('nonfreedep')
    
    # 检查非自由附加组件
    addon_patterns = [r'nonfree[-_]?addon', r'premium[-_]?feature']
    if any(any(re.search(pattern, f, re.I) for pattern in addon_patterns) for f in valid_files):
        antifeatures.append('nonfreeadd')
    
    # 检查NSFW内容
    nsfw_patterns = [r'\bnsfw\b', r'\badult\b', r'\bmature\b']
    if any(any(re.search(pattern, f, re.I) for pattern in nsfw_patterns) for f in valid_files):
        antifeatures.append('nsfw')
    
    # 检查用户数据收集
    data_collection_patterns = [r'collect[-_]?data', r'user[-_]?data', r'data[-_]?collection', r'收集数据']
    if any(any(re.search(pattern, f, re.I) for pattern in data_collection_patterns) for f in valid_files):
        antifeatures.append('tracking')
    
    # 检查已知漏洞
    vuln_patterns = [r'cve-\d+', r'vulnerability', r'exploit', r'security[-_]?issue', r'漏洞']
    if any(any(re.search(pattern, f, re.I) for pattern in vuln_patterns) for f in valid_files):
        antifeatures.append('knownvuln')
    
    # 去重
    return list(set(antifeatures))

def get_github_repo_info(repo_url, cache_dir=None):
    """获取GitHub仓库信息，支持缓存"""
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
    
    # 检查缓存
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cache_key = f"{owner}_{repo}"
        cache_path = Path(cache_dir) / f"{cache_key}.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                now = datetime.now()
                
                # 如果缓存在1天内，直接返回缓存数据
                if (now - cache_time) < timedelta(days=1):
                    print(f"Using cached data for GitHub repo: {repo_url}")
                    return {
                        'license': cache_data.get('license', ''),
                        'antifeatures': cache_data.get('antifeatures', []),
                        'updated_at': cache_data.get('updated_at', '')
                    }
            except (json.JSONDecodeError, KeyError):
                # 缓存文件损坏，继续获取
                print(f"Cache file for {repo_url} is corrupted")
                pass
    
    headers = {}
    if 'GITHUB_TOKEN' in os.environ:
        headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
    
    # 获取仓库信息
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get GitHub repo info: HTTP {response.status_code}")
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
        except Exception as e:
            print(f"Error checking vulnerabilities: {e}")
            pass
        
        # 检查上游依赖
        dependencies_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
        try:
            response = requests.get(dependencies_url, headers=headers)
            if response.status_code == 200:
                files = [f['name'].lower() for f in response.json()]
                antifeatures.extend(get_antifeatures_from_files(files))
        except Exception as e:
            print(f"Error checking dependencies: {e}")
            pass
        
        result = {
            'license': repo_info.get('license', {}).get('spdx_id', ''),
            'antifeatures': list(set(antifeatures)),  # 去重
            'updated_at': repo_info.get('updated_at', '')
        }
        
        # 缓存结果
        if cache_dir:
            try:
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'license': result['license'],
                    'antifeatures': result['antifeatures'],
                    'updated_at': result['updated_at']
                }
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f)
                print(f"Cached GitHub repo data for {repo_url}")
            except Exception as e:
                print(f"Failed to cache GitHub repo data: {e}")
        
        return result
    except Exception as e:
        print(f"Error getting GitHub repo info: {e}")
        return {
            'license': '',
            'antifeatures': [],
            'updated_at': ''
        }

def sort_antifeatures(antifeatures):
    """按照预定义的顺序排序antifeatures"""
    # 将antifeatures按照预定义的顺序排序
    sorted_antifeatures = []
    for feature in ANTIFEATURE_ORDER:
        if feature in antifeatures:
            sorted_antifeatures.append(feature)
    
    # 添加任何未在预定义顺序中的antifeatures（按字母顺序）
    for feature in sorted(antifeatures):
        if feature not in ANTIFEATURE_ORDER and feature not in sorted_antifeatures:
            sorted_antifeatures.append(feature)
    
    return sorted_antifeatures

def download_update_json(update_url, cache_dir=None):
    """下载update.json文件并支持缓存"""
    # 检查缓存
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        url_hash = hashlib.md5(update_url.encode()).hexdigest()
        cache_path = Path(cache_dir) / f"{url_hash}_update.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                now = datetime.now()
                
                # 如果缓存在1天内，直接返回缓存数据
                if (now - cache_time) < timedelta(days=1):
                    print(f"Using cached update.json for {update_url}")
                    return cache_data.get('data', {})
            except (json.JSONDecodeError, KeyError):
                # 缓存文件损坏，继续下载
                print(f"Cache file for update.json {update_url} is corrupted")
                pass
    
    # 下载update.json
    try:
        response = requests.get(update_url)
        if response.status_code != 200:
            print(f"Failed to download update.json: HTTP {response.status_code}")
            return {}
        
        update_json = response.json()
        
        # 缓存结果
        if cache_dir:
            try:
                cache_data = {
                    'timestamp': datetime.now().isoformat(),
                    'data': update_json
                }
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f)
                print(f"Cached update.json for {update_url}")
            except Exception as e:
                print(f"Failed to cache update.json: {e}")
        
        return update_json
    except Exception as e:
        print(f"Error downloading update.json: {e}")
        return {}

def create_track_json(repo_info, cache_dir=None):
    """创建track.json数据结构，支持缓存"""
    # 获取GitHub仓库信息
    github_info = get_github_repo_info(repo_info["url"], cache_dir)
    if not github_info:
        return None

    # 获取update.json内容
    update_json = download_update_json(repo_info["update_to"], cache_dir)
    
    zip_antifeatures = []
    module_version = ''
    min_magisk_version = ''
    
    # 如果有update.json并且有zipUrl，下载并分析模块文件
    if update_json and 'zipUrl' in update_json:
        # 下载并解析模块文件
        files = download_and_extract_zip(update_json['zipUrl'], cache_dir)
        if files:
            # 从zip文件内容检测antifeatures
            zip_antifeatures = get_antifeatures_from_files(files)
            
            # 检查模块版本和兼容性
            module_version = update_json.get('version', '')
            min_magisk_version = update_json.get('minMagisk', '')

    # 合并所有来源的 antifeatures 并按标准顺序排序
    antifeatures = sort_antifeatures(list(set(github_info.get('antifeatures', []) + zip_antifeatures)))

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
        "readme": readme_url
    }
    
    # 添加版本信息（如果有）
    if module_version:
        track["version"] = module_version
    
    if min_magisk_version:
        track["min_magisk"] = min_magisk_version
    
    # 只有当有antifeatures时才添加到track.json
    if antifeatures:
        track["antifeatures"] = antifeatures
        
    return track

def is_track_changed(old_track, new_track):
    """比较两个track数据，检查是否有实质性变化"""
    if not old_track:
        return True
    
    # 比较关键字段
    key_fields = ['license', 'version', 'min_magisk']
    for field in key_fields:
        if old_track.get(field) != new_track.get(field):
            return True
    
    # 比较antifeatures（已排序）
    old_antifeatures = sort_antifeatures(old_track.get('antifeatures', []))
    new_antifeatures = sort_antifeatures(new_track.get('antifeatures', []))
    if old_antifeatures != new_antifeatures:
        return True
    
    # 由于categories功能已弃用，不再比较categories
    return False

def update_tracks():
    """更新所有模块的track.json文件"""
    config = load_config()
    root_dir = Path(__file__).parent.parent
    
    # 创建缓存目录
    cache_dir = root_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    updated_modules = []
    total_modules = len(config["repositories"])
    
    for i, repo in enumerate(config["repositories"]):
        module_id = repo["module_id"]
        print(f"Processing [{i+1}/{total_modules}]: {module_id}")
        
        module_dir = root_dir / "modules" / module_id
        module_dir.mkdir(parents=True, exist_ok=True)
        
        track_path = module_dir / "track.json"
        
        # 读取现有的track.json（如果存在）
        old_track = None
        if track_path.exists():
            try:
                with open(track_path, 'r') as f:
                    old_track = json.load(f)
                    
                # 如果旧的track.json包含已弃用的categories字段，需要移除它
                if 'categories' in old_track:
                    del old_track['categories']
            except json.JSONDecodeError:
                old_track = None
        
        # 创建新的track数据
        new_track = create_track_json(repo, cache_dir)
        
        if not new_track:
            print(f"Failed to process repository: {repo['url']}")
            continue
        
        # 检查是否有变化
        if is_track_changed(old_track, new_track):
            # 写入新的track.json
            with open(track_path, 'w') as f:
                json.dump(new_track, f, indent=4)
            print(f"Updated track.json for {module_id}")
            updated_modules.append(module_id)
        else:
            print(f"No changes for {module_id}, skipping update")
    
    return updated_modules

if __name__ == "__main__":
    updated = update_tracks()
    if updated:
        print(f"Updated {len(updated)} modules: {', '.join(updated)}")
    else:
        print("No modules were updated")
