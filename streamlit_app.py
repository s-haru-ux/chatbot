import streamlit as st
from google import genai

# タイトルと説明文の表示
st.title("💬 Gemini Chatbot")
st.write(
    "GoogleのAIモデル「Gemini」を使用したシンプルなチャットボットです。"
    "使用するには、[Google AI Studio](https://aistudio.google.com/app/apikey)で取得できるGemini APIキーが必要です。"
)

# ユーザーからGemini APIキーを入力してもらう欄を表示
gemini_api_key = st.text_input("Gemini API Key", type="password")

if not gemini_api_key:
    st.info("継続するにはGemini APIキーを入力してください。", icon="🗝️")
else:
    # Gemini APIを呼び出すための「クライアント（準備）」を作成
    client = genai.Client(api_key=gemini_api_key)

    # 過去の会話履歴を保存する変数（session_state）を準備
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 画面にこれまでの会話履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 画面下に会話の入力欄を表示
    if prompt := st.chat_input("何か質問はありますか？"):

        # ユーザーの入力内容を履歴に追加して画面に表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 履歴データをGemini APIが理解できる形式に変換
        # ※OpenAIの「assistant」はGeminiでは「model」という名称に変わります
        gemini_contents = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        # APIからテキストが少しずつ返ってくる（ストリーミング）仕組みを作成
        def response_generator():
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=gemini_contents,
            )
            for chunk in response_stream:
                yield chunk.text

        # AIの回答を文字が打たれるように順次表示し、完成した文章を履歴に保存
        with st.chat_message("assistant"):
            response_text = st.write_stream(response_generator())

        st.session_state.messages.append({"role": "assistant", "content": response_text})
