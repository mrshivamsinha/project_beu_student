import streamlit as st
import pandas as pd

df = pd.read_csv("ranked_students.csv")

st.title("Student Performance & Rank Viewer")

reg = st.text_input("Enter Registration Number:")
if reg:
    student = df[df["registration_number"] == reg]
    if not student.empty:
        st.write(student)
    else:
        st.error("No student found!")
