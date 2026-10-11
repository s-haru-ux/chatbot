import streamlit as st
from google import genai

# 1. タイトルと説明文の表示
st.title("💬 Gemini Chatbot")
st.write(
    "GoogleのAI「Gemini」を使用したチャットボットです。"
    "使用するには、[Google AI Studio](https://aistudio.google.com/app/apikey)で取得できるGemini APIキーが必要です。"
)

# 2. ユーザーからGemini APIキーを入力してもらう欄を表示
gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("継続するにはGemini APIキーを入力してください。", icon="🗝️")
else:
    try:
        # 3. Gemini APIクライアントの作成
        client = genai.Client(api_key=gemini_api_key)

        # 4. お使いのAPIキーで利用可能なモデル一覧を自動取得する関数
        @st.cache_data(show_spinner="利用可能なモデルを取得中...")
        def get_available_models(api_key):
            temp_client = genai.Client(api_key=api_key)
            models = []
            for m in temp_client.models.list():
                # モデルID（名前）を取得
                model_id = m.name.replace("models/", "") if hasattr(m, "name") and m.name else str(m)
                # チャット（Gemini）に対応しているモデルのみ抽出
                if "gemini" in model_id.lower():
                    models.append(model_id)
            return models

        available_models = get_available_models(gemini_api_key)

        if not available_models:
            st.error("利用可能なGeminiモデルが見つかりませんでした。APIキーを確認してください。")
            st.stop()

        # 5. サイドバーでモデルを選択できるように設定（デフォルトはリスト内から自動選択）
        default_index = 0
        for i, m in enumerate(available_models):
            if "flash" in m.lower():
                default_index = i
                break

        selected_model = st.sidebar.selectbox("使用モデル", available_models, index=default_index)

    except Exception as e:
        st.error(f"APIキーの検証またはモデル一覧の取得に失敗しました: {e}")
        st.stop()

    # 6. 会話履歴を保存する変数を準備
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 7. 画面にこれまでの会話履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 8. 会話の入力欄を表示
    if prompt := st.chat_input("何か質問はありますか？"):

        # 9. ユーザーの入力を履歴に追加して表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 10. 履歴データをGemini API用の形式に変換
        gemini_contents = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        # 11. AIから文字を順次受け取る関数（ストリーミング処理）
        def response_generator():
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=gemini_contents,
            )
            for chunk in response_stream:
                yield chunk.text

        # 12. AIの回答を画面に表示し、履歴に保存
        with st.chat_message("assistant"):
            try:
                response_text = st.write_stream(response_generator())
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"回答生成中にエラーが発生しました: {e}")
