import pandas as pd
import streamlit as st
from pandas.api.types import (
    CategoricalDtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.title("Kablo listesi")

st.write("""
    Kablo listelerini web üzerinden görmek için tasarlandı.
"""

)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    modify = st.checkbox("Filtre ekle")

    if not modify:
        return df
    multi_css=f'''
            <style>
            .stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
            .stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"Seçiniz";}}
            </style>
            '''
    st.markdown(multi_css, unsafe_allow_html=True)    
    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Veri üzerinde filtrele", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            #if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
            if (df[column].nunique()>0):
                user_cat_input = right.multiselect(
                    f"{column} içindeki değerler",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"{column} içinde ara",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df


df=pd.read_excel(open('data.xlsx',encoding='utf-8'),
              sheet_name='Sayfa1')  

st.dataframe(filter_dataframe(df))



