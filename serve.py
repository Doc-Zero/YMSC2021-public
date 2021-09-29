from bs4 import BeautifulSoup as bs
import requests as req
import pandas as pd
import re
import streamlit as st
from urllib.parse import quote
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder

def _max_width_():
    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

def fetch_data(max_rows=99, sortmode=1, searchkey="", link=False, link_col="바로가기"):
    url="http://ymsc2021.org/poster.asp?xrow={}&xsearch={}&xquery={}".format(max_rows, sortmode, quote(searchkey, encoding='cp949'))
    body=bs(req.get(url).text, 'lxml').find_all("table", attrs={"class": "boardTable tc"})[0].find_all("tr")
    body_rows=body[1:]
    headings=[(item.text).rstrip("\n") for item in body[0].find_all("th")]
    all_rows=[[re.sub("(\xa0)|(\n)","",row_item.text) for row_item in body_rows[row_num].find_all("td")] for row_num in range(len(body_rows))]
    rearr_headings=headings[-2:]+headings[:-2]
    if all_rows==[['Data not found.']]:
        all_rows=[['검색 결과 없음']*len(headings)]
        return pd.DataFrame(data=all_rows, columns=headings)[rearr_headings], None
    df=pd.DataFrame(data=all_rows, columns=headings)[rearr_headings].astype({headings[-2]:int, headings[-1]:int}).sort_values(by=rearr_headings[0], ascending=False)
    gb=None
    if link:
        df.insert(len(headings)-1, link_col, df['주제'].map(lambda x: quote(x[:40], encoding='cp949'), na_action='ignore'))
        gb=GridOptionsBuilder.from_dataframe(df)
        gb.configure_column("바로가기", headerName='Link', cellRenderer=JsCode('''function(params) {return '<a href=\"'+'http://ymsc2021.org/poster.asp?xsearch=3&xquery='+params.value+'\" target=\"_blank\" rel=\"noopener noreferrer\">링크</a>'}'''), width=300)
    return df, gb

_max_width_()
st.title('2021 YMSC 포스터 발표 대회 - 완료')
st.write('[로그인](http://ymsc2021.org/member/Login.asp)')
option_1=st.sidebar.selectbox('검색 필드', ['발표자', '소속', '주제'])
option_2=st.sidebar.text_input('검색 키워드', "")
#TO DO : add button to refresh
#st.button('🔄', on_click=)
if option_2 != "":
    st.subheader("검색결과")
else:
    st.subheader("최종 리더보드")
st.write("-----")
df, gb=fetch_data(sortmode={'발표자':1, '소속':2, '주제':3}[option_1],searchkey=option_2, link=True)
if gb is None:
    gb=GridOptionsBuilder.from_dataframe(df)
AgGrid(df, gridOptions=gb.build(), allow_unsafe_jscode=True)
st.write("-----")
st.write("2021-09-28 오후 12:30 (KST) : 모든 행사가 끝나, 더이상 좋아요가 되지 않습니다!\n 대회에 참여하신 모든 학우분들 수고하셨습니다.")
st.write("2021-09-29 오후 05:00 (KST) : 2022년에 동일한 행사가 열릴 때를 대비하여, 가끔 업데이트가 있을 예정입니다!")
