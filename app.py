import os
import time
import json
import streamlit as st
import requests
from dotenv import load_dotenv

# 1. 環境変数とページ設定
load_dotenv()
st.set_page_config(page_title="FaceStatus", page_icon="🎮", layout="centered")

API_KEY = os.getenv("YOUCAM_API_KEY")
FILE_API_URL = os.getenv("YOUCAM_FILE_API_URL")
TASK_API_URL = os.getenv("YOUCAM_TASK_API_URL")

# YouCam公式サンプル画像URLのプリセット
PRESET_IMAGES = [
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_01_5b5defd339.png",
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_02_875f3b51a3.png",
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_03_b1d98441a6.png",
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_04_1b6339716b.png",
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_05_d6671299a6.png",
    "https://plugins-media.makeupar.com/strapi/assets/skin_analysis_06_c9136eea8f.png"
]

# セッション状態（State）の初期化
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "preset"
if "current_target" not in st.session_state:
    st.session_state.current_target = PRESET_IMAGES[0]
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0a192f"
if "text_color" not in st.session_state:
    st.session_state.text_color = "#00efff"

# 2. YouCam API 接続コアロジック（ハイブリッド仕様）
def run_face_scan_hybrid(target):
    dst_actions = ["dark_circle_v2", "moisture", "wrinkle"]
    headers_json = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # --- 📁 パターンA: ローカルファイル（bytes）の場合（セキュア3ステップ） ---
    if not isinstance(target, str):
        try:
            file_meta_payload = {
                "files": [
                    {
                        "content_type": "image/jpeg",
                        "file_name": "face_status_input.jpg",
                        "file_size": len(target)
                    }
                ]
            }
            st.toast("🔒 [1/4] 画像のメタデータを登録中...")
            meta_resp = requests.post(FILE_API_URL, headers=headers_json, json=file_meta_payload)
            if not meta_resp.ok:
                st.error(f"メタデータ登録に失敗: {meta_resp.status_code}")
                return None
                
            meta_data = meta_resp.json().get("data", {}).get("files", [{}])[0]
            file_id = meta_data.get("file_id")
            put_request_info = meta_data.get("requests", [{}])[0]
            
            put_url = put_request_info.get("url")
            put_headers = put_request_info.get("headers", {})

            st.toast("🛰️ [2/4] セキュアストレージへ画像をPUT送信中...")
            put_resp = requests.put(put_url, headers=put_headers, data=target)
            if not put_resp.ok:
                st.error(f"ストレージへの直接アップロードに失敗: {put_resp.status_code}")
                return None

            st.toast("🧠 [3/4] 登録完了。AI解析タスクを作成中...")
            task_payload = {
                "src_file_id": file_id,
                "dst_actions": dst_actions,
                "miniserver_args": {"enable_mask_overlay": False},
                "format": "json"
            }
            task_resp = requests.post(TASK_API_URL, headers=headers_json, json=task_payload)

        except Exception as e:
            st.error(f"セキュアアップロード中に例外が発生しました: {e}")
            return None

    # --- 🔗 パターンB: パブリックURL（文字列）指定方式 ---
    else:
        st.toast("🚀 [1/2] 公開URLで解析タスクを作成中...")
        task_payload = {
            "src_file_url": target,
            "dst_actions": dst_actions,
            "miniserver_args": {"enable_mask_overlay": False},
            "format": "json",
            "pf_camera_kit": False
        }
        task_resp = requests.post(TASK_API_URL, headers=headers_json, json=task_payload)

    # --- 🔄 共通処理: タスクの起動確認 ＆ ポーリング ---
    if not task_resp.ok:
        st.error(f"AIタスク作成に失敗しました: {task_resp.status_code} {task_resp.reason}")
        return None
        
    task_id = task_resp.json().get('data', {}).get('task_id')
    
    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        time.sleep(2)
        st.toast(f"⏳ [4/4] AIが顔面をスキャン中... (試行 {attempt} 回目)")
        poll_resp = requests.get(f"{TASK_API_URL}/{task_id}", headers={"Authorization": f"Bearer {API_KEY}"})
        if not poll_resp.ok:
            continue
        payload = poll_resp.json()
        status = payload.get('data', {}).get('task_status')
        
        if status == 'success':
            st.toast("✨ 解析成功！ステータスを同期します。")
            return payload.get('data', {}).get('results', {})
        if status == 'error':
            st.error("API内部で解析エラーが発生しました。")
            return None
            
    st.error("解析がタイムアウトしました。")
    return None

# 3. UI / アプリケーション本編
st.title("🎮 FaceStatus MVP")
st.subheader("〜 顔色で変わるエンジニア生存RPG 〜")

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("### ⚙️ 画像ソースの選択")
tab1, tab2, tab3 = st.tabs(["👥 サンプル被験者", "🔗 任意の画像URLを指定", "📁 ローカルからアップロード"])

with tab1:
    cols = st.columns(6)
    for i, url in enumerate(PRESET_IMAGES):
        with cols[i]:
            if st.button(f"被験者 {chr(65+i)}", key=f"btn_{i}", use_container_width=True):
                st.session_state.input_mode = "preset"
                st.session_state.current_target = url
                st.session_state.scan_results = None
                st.rerun()

with tab2:
    current_url = st.session_state.current_target if isinstance(st.session_state.current_target, str) else PRESET_IMAGES[0]
    url_input = st.text_input("インターネット上の画像URLを入力してください", value=current_url)
    if url_input != current_url:
        st.session_state.input_mode = "url"
        st.session_state.current_target = url_input
        st.session_state.scan_results = None

with tab3:
    uploaded_file = st.file_uploader("PCやスマホから顔写真をアップロード（JPG/PNG）", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.session_state.input_mode = "upload"
        st.session_state.current_target = uploaded_file.read()

st.write("")
trigger_scan = st.button("🚀 選択した画像でスキャン開始（属性判定）", use_container_width=True)

if trigger_scan:
    if not API_KEY or not FILE_API_URL or not TASK_API_URL:
        st.warning(".envファイルにAPIキーやURLが正しく設定されているか確認してください。")
    else:
        results = run_face_scan_hybrid(st.session_state.current_target)
        if Hacker_results := results:
            st.session_state.scan_results = Hacker_results
            
            output_list = Hacker_results.get("output", [])
            all_data = next((item for item in output_list if item.get("type") == "all"), {})
            hp = int(all_data.get("score", 50))
            
            if hp >= 70:
                st.session_state.bg_color = "#0a192f"
                st.session_state.text_color = "#00efff"
            else:
                st.session_state.bg_color = "#2b0000"
                st.session_state.text_color = "#ff3333"
            st.rerun()

st.write("---")

st.markdown("### 🪪 ギルド登録証（ステータスシート）")
col_left, col_right = st.columns([4, 6])

with col_left:
    if st.session_state.input_mode == "upload":
        st.image(st.session_state.current_target, caption="📷 持ち込み顔写真（ローカル）", use_container_width=True)
    else:
        st.image(st.session_state.current_target, caption="📷 登録顔写真（URL指定）", use_container_width=True)

with col_right:
    if st.session_state.scan_results:
        results = st.session_state.scan_results
        output_list = results.get("output", [])
        
        scores = {item.get("type"): item.get("ui_score", 0) for item in output_list if "ui_score" in item}
        
        dark_circle = scores.get("dark_circle_v2", 0)
        moisture = scores.get("moisture", 0)
        skin_age = next((item.get("score") for item in output_list if item.get("type") == "skin_age"), "??")
        
        all_data = next((item for item in output_list if item.get("type") == "all"), {})
        hp = int(all_data.get("score", 50))
        mp = moisture
        
        if hp >= 70:
            st.markdown("## 🧙‍♂️ 属性：【大賢者】")
            st.markdown("<p style='color:#00efff;'><b>バフ効果:</b> 『神コード量産体制』。脳が冴え渡っています。今すぐコミットしましょう！</p>", unsafe_allow_html=True)
        else:
            st.markdown("## 🧟 属性：【瀕死のゾンビ】")
            st.markdown("<p style='color:#ff3333;'><b>デバフ効果:</b> 『無限バグ生成の呪い』。クマが深く危険域です。今すぐ寝てください！</p>", unsafe_allow_html=True)
            
        st.metric(label="❤️ 現在のHP (総合体力)", value=f"{hp} / 100")
        st.progress(hp / 100)
        
        st.metric(label="🔷 現在のMP (集中力)", value=f"{mp} / 100")
        st.progress(mp / 100)
        
        st.markdown(f"**⏳ 推定肌年齢**: `{skin_age}` 歳")
        
        with st.expander("📊 詳細なステータスログを見る"):
            st.write(f"・徹夜度（クマの深さの指標）: {dark_circle}")
            st.write(f"・カサカサ度（肌水分量の指標）: {moisture}")
    else:
        st.info("上のコントロールパネルから画像を選んで「🚀 スキャン開始」ボタンを押すと、ここにあなたの冒険者ステータスが同期されます。")
