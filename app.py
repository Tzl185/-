import streamlit as st
import pandas as pd
import zipfile
import io
import os

st.title("工资预算汇总工具")
st.markdown("上传包含多个 Excel 文件的 `.zip` 文件，程序将汇总‘预算单位’与14类工资数据。")

uploaded_file = st.file_uploader("请选择一个 .zip 文件", type="zip")

if uploaded_file:
    with zipfile.ZipFile(uploaded_file, "r") as z:
        all_data = []

        for filename in z.namelist():
            if filename.endswith('.xls') or filename.endswith('.xlsx'):
                with z.open(filename) as file:
                    try:
                        df = pd.read_excel(file, header=3)

                        budget_unit_col = df.columns[1]
                        wage_cols = df.columns[16:30]

                        df_filtered = df[[budget_unit_col] + list(wage_cols)]
                        df_filtered[wage_cols] = df_filtered[wage_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
                        df_grouped = df_filtered.groupby(budget_unit_col).sum()
                        all_data.append(df_grouped)

                        st.success(f"{filename} 读取成功")

                    except Exception as e:
                        st.warning(f"{filename} 读取失败：{e}")

        if all_data:
            df_all = pd.concat(all_data)
            df_final = df_all.groupby(df_all.index).sum()
            st.subheader("汇总结果预览")
            st.dataframe(df_final)

            output = io.BytesIO()
            df_final.to_excel(output)
            st.download_button("下载汇总结果", data=output.getvalue(), file_name="汇总结果.xlsx")
        else:
            st.error("未能成功读取任何数据文件")
