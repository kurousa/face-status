# 🎮 FaceStatus

> **〜 顔色で変わるエンジニア生存RPG 〜**

`FaceStatus` は、YouCam Skin Analysis API を活用してユーザーの顔写真を解析し、日々のデスクワークや徹夜によるダメージをRPG風のステータスシート（ギルド登録証）として視覚化する Streamlit アプリケーションです。

---

## 🚀 主な機能

- **マルチ画像ソース選択**:
  - **サンプル被験者**: プリセットされたサンプル画像（A〜F）からワンクリックで手軽に試せます。
  - **画像URL指定**: インターネット上の公開画像URLを入力して解析できます。
  - **ローカルアップロード**: 手元のPCやスマホからJPG/PNG画像をアップロードして直接解析できます（セキュアな3ステップアップロード仕様に対応）。
- **リアルタイムAI肌解析 (YouCam API)**:
  - クマの深さ（`dark_circle_v2`）、肌水分量（`moisture`）、シワ（`wrinkle`）などを裏側でAI解析します。
- **動的なRPGステータス判定**:
  - 解析結果に基づいて、あなたの「現在のHP（総合体力）」、「現在のMP（集中力）」、「推定肌年齢」を算出します。
- **生存状況に応じた動的UIテーマ変化**:
  - **HP 70以上 【大賢者】**: 冴え渡った脳を象徴するサイバーブルーのテーマ。バフ効果『神コード量産体制』。
  - **HP 70未満 【瀕死のゾンビ】**: 限界を迎えた脳を象徴するダークレッドのテーマ。デバフ効果『無限バグ生成の呪い』。

---

## 🛠️ 技術スタック

- **ランタイム / パッケージ管理**: [uv](https://github.com/astral-sh/uv) (Python >= 3.13)
- **UI フレームワーク**: [Streamlit](https://streamlit.io/)
- **API 通信**: [Requests](https://requests.readthedocs.io/)
- **外部サービス**: [YouCam Skin Analysis API](https://www.perfectcorp.com/)

---

## 📦 セットアップと起動方法

本プロジェクトは、高速なPythonパッケージマネージャーである `uv` を使用して開発されています。

### 1. 環境変数の設定
プロジェクトのルートディレクトリに `.env` ファイルを作成し、必要なAPI情報を記述します。`.env.example` をコピーして編集するのが便利です。

```bash
cp .env.example .env
```

`.env` の記述内容：
```env
YOUCAM_API_KEY=your_api_key_here
YOUCAM_FILE_API_URL=https://yce-api-01.makeupar.com/s2s/v2.1/file/skin-analysis
YOUCAM_TASK_API_URL=https://yce-api-01.makeupar.com/s2s/v2.1/task/skin-analysis
```

> [!IMPORTANT]
> `YOUCAM_API_KEY` には有効な Perfect Corp. YouCam API キーを設定してください。

### 2. アプリケーションの起動
`uv` コマンドを使用して、依存関係の解決とアプリケーションの起動をワンコマンドで実行します。

```bash
uv run streamlit run app.py
```

起動後、自動的にブラウザが立ち上がり `http://localhost:8501` にてアプリにアクセスできます。

---

## 📁 ディレクトリ構造

```text
├── .env.example         # 環境変数のサンプルファイル
├── app.py               # Streamlit アプリケーションのメインソースコード
├── pyproject.toml       # プロジェクト設定および依存関係の定義
├── README.md            # 本ドキュメント
└── test_api.py          # API接続テスト用スクリプト
```
