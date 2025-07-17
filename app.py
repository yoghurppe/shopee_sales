import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="LUCIDO売上比較", layout="wide")
st.title("🛒 Shopee LUCIDO売上比較（台湾・フィリピン・ベトナム）")

brand = st.text_input("🔍 ブランド名を入力してください", "LUCIDO")

@st.cache_data(ttl=3600)
def fetch_items(market, url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    titles, solds = [], []

    for item in soup.select('div.shopee-search-item-result__item'):
        title_tag = item.find('div', attrs={'data-sqe': 'name'})
        sold_tag = item.find('div', string=lambda s: s and 'sold' in s)

        if title_tag and sold_tag:
            titles.append(title_tag.get_text(strip=True))
            solds.append(sold_tag.get_text(strip=True))

    return pd.DataFrame({"商品名": titles, "販売数": solds})


if st.button("📊 データ取得"):
    urls = {
        "台湾": f"https://shopee.tw/search?keyword={brand}",
        "フィリピン": f"https://shopee.ph/search?keyword={brand}",
        "ベトナム": f"https://shopee.vn/search?keyword={brand}",
    }

    all_results = []
    for country, url in urls.items():
        df = fetch_items(country, url)
        df["国"] = country
        all_results.append(df)

    result = pd.concat(all_results, ignore_index=True)
    st.dataframe(result)
    st.download_button("⬇ CSVダウンロード", result.to_csv(index=False), file_name="lucido_sales.csv")
