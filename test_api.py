import os
import time
import json
import requests
from dotenv import load_dotenv

# 1. 環境変数の読み込み
load_dotenv()

API_KEY = os.getenv("YOUCAM_API_KEY")
BASE_URL = os.getenv("YOUCAM_SKIN_API_URL")

if not API_KEY or not BASE_URL:
    print("❌ エラー: .env ファイルの環境変数が不足しています。")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def start_skin_analysis_task(image_url: str) -> str:
    """YouCam APIに解析タスクを要求し、task_idを取得する"""
    payload = {
        "src_file_url": image_url,
        "dst_actions": ["dark_circle_v2", "moisture", "wrinkle"],
        "miniserver_args": {
            "enable_mask_overlay": False
        },
        "format": "json",
        "pf_camera_kit": False
    }
    
    print("🚀 [1/2] 解析タスクを開始します...")
    print(BASE_URL)
    print(payload)
    resp = requests.post(BASE_URL, headers=HEADERS, json=payload)
    print(resp.json())
    
    if not resp.ok:
        raise RuntimeError(f"タスク開始要求に失敗: {resp.status_code} {resp.reason} {resp.text}")
        
    data = resp.json() if resp.content else {}
    task_id = data.get('data', {}).get('task_id')
    
    if not task_id:
        raise RuntimeError('JSONから task_id が見つかりません: ' + json.dumps(data))
        
    print('✅ タスク受付成功。ID =', task_id)
    return task_id

def poll_skin_analysis_result(task_id: str, interval_s=2, max_attempts=30) -> dict:
    """タスクの完了を定期確認（ポーリング）し、結果のJSONを返す"""
    print("⏳ [2/2] AI解析の完了を待っています（ポーリング中）...")
    
    for attempt in range(1, max_attempts + 1):
        poll_url = f"{BASE_URL}/{task_id}"
        resp = requests.get(poll_url, headers=HEADERS)
        
        if not resp.ok:
            raise RuntimeError(f"ポーリングに失敗: {resp.status_code} {resp.reason}")
            
        payload = resp.json() if resp.content else {}
        status = payload.get('data', {}).get('task_status')
        
        print(f" 🔄 試行 {attempt}回目: ステータス = {status}")
        
        if status == 'success':
            print('✨ AI解析完了！')
            return payload
        if status == 'error':
            raise RuntimeError('API内部でタスクが失敗しました: ' + json.dumps(payload))
            
        time.sleep(interval_s)
        
    raise RuntimeError('タイムアウト: 最大試行回数を超えました')

if __name__ == '__main__':
    # テスト用のサンプル画像URL（公式のPlaygroundのもの）
    test_image = "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_01_5b5defd339.png"
    
    try:
        # 1. タスク開始
        t_id = start_skin_analysis_task(test_image)
        # 2. 結果取得までループ
        final_response = poll_skin_analysis_result(t_id)
        
        # 3. 結果のパーステスト
        results = final_response.get('data', {}).get('results', {})
        # ※実際の返却データの構造に合わせてキーを調整してください
        print("\n=== [パース成功！抽出データ] ===")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print('❌ 処理エラー:', e)