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
    # 3. Gemini APIを呼び出すためのクライアントを作成
    client = genai.Client(api_key=gemini_api_key)

    # 4. 会話履歴を保存する変数を準備
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 5. 画面にこれまでの会話履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. 会話の入力欄を表示
    if prompt := st.chat_input("何か質問はありますか？"):

        # 7. ユーザーの入力を履歴に追加して表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 8. 履歴データをGemini API用の形式に変換
        gemini_contents = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        # 9. AIから文字を順次受け取る関数（ストリーミング処理）
        def response_generator():
            response_stream = client.models.generate_content_stream(
                model="gemini-1.5-flash",  # ← 確実に動作するモデル名に変更しました
                contents=gemini_contents,
            )
            for chunk in response_stream:
                yield chunk.text

        # 10. AIの回答を画面に表示し、履歴に保存
        with st.chat_message("assistant"):
            response_text = st.write_stream(response_generator())

        st.session_state.messages.append({"role": "assistant", "content": response_text})import streamlit as st
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
    # 3. Gemini APIを呼び出すための「クライアント（接続準備）」を作成
    client = genai.Client(api_key=gemini_api_key)

    # 4. 会話履歴を保存する変数（session_state）を準備
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 5. 画面にこれまでの会話履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. 画面下に会話の入力欄を表示
    if prompt := st.chat_input("何か質問はありますか？"):

        # 7. ユーザーの入力内容を履歴に追加して画面に表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 8. 会話履歴をGemini APIが理解できる形式（user/model）に変換
        gemini_contents = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        # 9. APIから文字を順次受け取る関数（ストリーミング表示用）
        def response_generator():
            response_stream = client.models.generate_content_stream(
                model="gemini-2.0-flash",  # 最新の標準モデルを指定
                contents=gemini_contents,
            )
            for chunk in response_stream:
                yield chunk.text

        # 10. AIの回答を文字が打たれるように順次表示し、履歴に保存
        with st.chat_message("assistant"):
            response_text = st.write_stream(response_generator())

        st.session_state.messages.append({"role": "assistant", "content": response_text})
