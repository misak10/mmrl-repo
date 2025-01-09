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
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
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
    antifeatures = []
    
    # 检查广告相关文件
    ad_patterns = [r'\bad[s]?\b', r'\badvertisement[s]?\b', r'\badvert[s]?\b']
    if any(any(re.search(pattern, f) for pattern in ad_patterns) for f in files):
        antifeatures.append('ads')
    
    # 检查追踪相关文件 
    track_patterns = [r'\btrack(er|ing)?\b', r'\banalytics?\b', r'\bstatistics?\b', r'\btelemetry\b']
    if any(any(re.search(pattern, f) for pattern in track_patterns) for f in files):
        antifeatures.append('tracking')
    
    # 检查非自由网络服务
    service_patterns = [
        r'\bgoogle[-_]?(analytics|ads|play)\b',
        r'\bfacebook[-_]?sdk\b',
        r'\bamazon[-_]?aws\b',
        r'\bproprietary[-_]?api\b'
    ]
    if any(any(re.search(pattern, f) for pattern in service_patterns) for f in files):
        antifeatures.append('nonfreenet')
    
    # 检查非自由操作系统依赖
    os_patterns = [r'\bwindows[-_]?(dll|exe|sys)\b', r'\bios[-_]?(framework|lib)\b']
    if any(any(re.search(pattern, f) for pattern in os_patterns) for f in files):
        antifeatures.append('nonfreeos')
    
    # 检查非自由媒体
    nonfree_media = ['.mp3', '.aac', '.wma', '.m4p', '.m4v']
    if any(f.lower().endswith(tuple(nonfree_media)) for f in files):
        antifeatures.append('nonfreemedia')
    
    return antifeatures

def get_github_repo_info(repo_url):
    # 从URL中提取owner和repo名称
    match = re.match(r'https://github.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        return None
    
    owner, repo = match.groups()
    headers = {}
    if 'GITHUB_TOKEN' in os.environ:
        headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
    
    # 获取仓库信息
    api_url = f'https://api.github.com/repos/{owner}/{repo}'
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return None
    
    repo_info = response.json()
    
    # 检查仓库状态
    antifeatures = []
    
    # 检查是否已归档
    if repo_info.get('archived', False):
        antifeatures.append('archived')
    
    # 检查最后更新时间
    last_updated = datetime.strptime(repo_info['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
    last_updated = last_updated.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if (now - last_updated).days > 30:
        antifeatures.append('unmaintained')
    
    # 检查是否已废弃
    if repo_info.get('deprecated', False):
        antifeatures.append('deprecated')
    
    # 检查是否是私有仓库或闭源
    if repo_info.get('private', False) or not repo_info.get('license'):
        antifeatures.append('proprietary')
    
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
        'updated_at': repo_info['updated_at']
    }

def get_module_categories(files):
    categories = []
    
    # Zygisk模块
    if any('zygisk' in f for f in files):
        categories.append('Zygisk')
    
    # 脚本模块
    if any(f in files for f in ['service.sh', 'post-fs-data.sh']):
        categories.append('Script')
    
    # 系统模块
    if any('system' in f or 'system.prop' in f for f in files):
        categories.append('System')
    
    # 主题模块
    if any('theme' in f or 'overlay' in f for f in files):
        categories.append('Theme')
    
    # 字体模块
    if any('font' in f or '.ttf' in f or '.otf' in f for f in files):
        categories.append('Font')
    
    # 音频模块
    if any('audio' in f or 'sound' in f or '.wav' in f or '.mp3' in f for f in files):
        categories.append('Audio')
    
    # 框架模块
    if any('framework' in f or 'xposed' in f for f in files):
        categories.append('Framework')
    
    # 安全模块
    if any('security' in f or 'privacy' in f or 'protect' in f for f in files):
        categories.append('Security')
    
    # 网络模块
    if any('network' in f or 'wifi' in f or 'proxy' in f for f in files):
        categories.append('Network')
    
    # 性能模块
    if any('performance' in f or 'boost' in f or 'tweak' in f for f in files):
        categories.append('Performance')
    
    # 实用工具
    if any('util' in f or 'tool' in f for f in files):
        categories.append('Utility')
    
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
        "readme": f"https://raw.githubusercontent.com/{repo_info['url'].split('github.com/')[1]}/main/README.md"
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
