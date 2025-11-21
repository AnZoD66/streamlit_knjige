import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


def ucitaj_podatke(sheet_url, sheet_name):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes = scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

SHEET_URL = st.secrets["sheet_url"]
SHEET_NAME = "list"
df, worksheet = ucitaj_podatke(SHEET_URL, SHEET_NAME)

df["Godina"] = pd.to_numeric(df["Godina"])
df["Ocjena"] = pd.to_numeric(df["Ocjena"])

st.title("Moje najdraže knjige.")

st.subheader("Trenutni popis knjiga.")
st.dataframe(df)

st.subheader("Dodajte novu knjigu")
naslov = st.text_input("Naslov")
autor = st.text_input("Autor")
godina = st.number_input("Godina", step=1, format="%d")
zanr = st.text_input("Žanr")
ocjena = st.slider("Ocjena", 1, 10)

if st.button("Dodajte knjigu"):
    novi_red = [naslov, autor, int(godina), zanr, ocjena]
    worksheet.append_row(novi_red)
    st.success("Uspješno ste dodali knjigu!")
    st.rerun()

st.subheader("Pretražite knjige")
filtrirani = df.copy()

autor_filt = st.text_input("Pretražite po autoru")
zanr_filt = st.text_input("Pretražite po žanru")
godina_filt = st.number_input("Pretražite po godini", step=1, format="%d")

if autor_filt:
    filtrirani = filtrirani[filtrirani["Autor"].str.contains(autor_filt, case=False)]

if zanr_filt:
    filtrirani = filtrirani[filtrirani["Žanr"].str.contains(zanr_filt, case=False)]

if godina_filt:
    filtrirani = filtrirani[filtrirani["Godina"] == int(godina_filt)]

st.dataframe(filtrirani)

st.subheader("Brisanje knjiga")

knjige_opcije = df.apply(
    lambda row: f"{row['Naslov']}-{row['Autor']} ({row['Godina']})",
    axis=1
).tolist()
knjige_za_brisanje = st.selectbox("Odaberite knjigu za brisanje", options=knjige_opcije)

if st.button("Obrišite knjigu"):
    for idx, row in df.iterrows():
        if f"{row['Naslov']}-{row['Autor']} ({row['Godina']})" == knjige_za_brisanje:
            worksheet.delete_rows(idx + 2)
            st.success("Knjiga je uspješno izbrisana!")
            st.rerun()

st.subheader("Top 5 knjiga")

top5 = df.sort_values(by = "Ocjena", ascending=False).head(5)
st.table(top5)









