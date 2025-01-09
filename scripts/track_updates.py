import json
import os
from datetime import datetime
from pathlib import Path
import requests
import re

def load_config():
    config_path = Path(__file__).parent.parent / "json" / "track_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

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
    
    # 获取仓库内容以检查模块类型
    contents_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
    response = requests.get(contents_url, headers=headers)
    if response.status_code != 200:
        return None
    
    contents = response.json()
    
    # 确定模块分类
    categories = []
    files = [f.get('name', '').lower() for f in contents]
    
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
    
    return {
        'license': repo_info.get('license', {}).get('spdx_id', ''),
        'categories': list(set(categories))  # 去重
    }

def create_track_json(repo_info):
    # 获取GitHub仓库信息
    github_info = get_github_repo_info(repo_info["url"])
    if not github_info:
        return None

    # 处理 antifeatures
    antifeatures = []
    if repo_info.get("antifeatures"):
        for feature, enabled in repo_info["antifeatures"].items():
            if enabled:
                antifeatures.append(feature)

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
        "categories": github_info["categories"],
        "readme": f"https://raw.githubusercontent.com/{repo_info['url'].split('github.com/')[1]}/main/README.md"
    }
    
    # 只有当有启用的 antifeatures 时才添加到 track.json
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
