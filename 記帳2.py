import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# =========================
# Page Config (手機感UI)
# =========================
st.set_page_config(
    page_title="記帳",
    page_icon="💰",
    layout="centered"
)

# =========================
# iOS風CSS
# =========================
st.markdown("""
<style>
/* 全局背景 */
[data-testid="stAppViewContainer"] {
    background-color: #f5f5f7;
}

/* 卡片 */
.card {
    background: white;
    padding: 16px;
    border-radius: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

/* 標題 */
.title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* 按鈕 */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    padding: 10px;
    background: #007aff;
    color: white;
    font-weight: bold;
}

/* input */
.stTextInput>div>div>input {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DB
# =========================
conn = sqlite3.connect("money.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type TEXT,
    category TEXT,
    amount REAL,
    note TEXT
)
""")
conn.commit()

# =========================
# Title
# =========================
st.markdown('<div class="title">💰 我的記帳</div>', unsafe_allow_html=True)

# =========================
# Tabs (像App)
# =========================
tab1, tab2, tab3 = st.tabs(["➕ 新增", "📊 統計", "📒 記錄"])

# =========================
# 新增
# =========================
with tab1:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    date = st.date_input("日期", datetime.today())
    t = st.selectbox("類型", ["支出", "收入"])
    cat = st.selectbox("分類", ["餐飲","交通","娛樂","投資","薪水","購物","其他"])
    amount = st.number_input("金額", min_value=0.0)
    note = st.text_input("備註")

    if st.button("新增記錄"):
        c.execute("INSERT INTO records VALUES (NULL,?,?,?,?,?)",
                  (str(date), t, cat, amount, note))
        conn.commit()
        st.success("已新增")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 統計
# =========================
with tab2:

    df = pd.read_sql_query("SELECT * FROM records", conn)

    if len(df) == 0:
        st.info("沒有資料")
    else:
        income = df[df["type"]=="收入"]["amount"].sum()
        expense = df[df["type"]=="支出"]["amount"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("收入", income)
        col2.metric("支出", expense)
        col3.metric("結餘", income-expense)

        # pie chart
        exp = df[df["type"]=="支出"].groupby("category")["amount"].sum().reset_index()

        if len(exp) > 0:
            fig = px.pie(exp, names="category", values="amount")
            st.plotly_chart(fig, use_container_width=True)

# =========================
# 記錄
# =========================
with tab3:

    df = pd.read_sql_query("SELECT * FROM records ORDER BY id DESC", conn)

    if len(df) == 0:
        st.info("沒有紀錄")
    else:
        for _, r in df.iterrows():
            sign = "-" if r['type']=="支出" else "+"

            st.markdown(f"""
            <div class="card">
                <b>{r['category']}</b> ｜ {r['date']}<br>
                {r['note']}<br>
                <span style='color:#007aff;font-size:18px;'>
                    {sign}{r['amount']}
                </span>
            </div>
            """, unsafe_allow_html=True)
