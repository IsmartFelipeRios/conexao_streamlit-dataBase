import streamlit as st
from app import make_df

query = st.text_input('SQL query')

if query:
    df = make_df(query)
    
    # Print results.
    try:
        st.dataframe(df)
    except:
        pass

else: st.warning('Coloque a query na caixa')

st.button("rerun")
if st.button("Clean Cach",):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("All cache cleared!")
