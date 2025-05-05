import pandas as pd
df = pd.read_csv("students_data.csv")

print(df.columns.tolist())

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df = df.dropna(subset=["sgpa", "cur._cgpa"])

df["sgpa"] = pd.to_numeric(df["sgpa"], errors="coerce")
df["cur._cgpa"] = pd.to_numeric(df["cur._cgpa"], errors="coerce")

df = df.drop_duplicates()


# University rank (higher CGPA = better rank)
df["university_rank"] = df["cur._cgpa"].rank(method="min", ascending=False).astype(int)

# Branch rank (ranking within the same branch)
df["branch_rank"] = df.groupby("branch_name")["cur._cgpa"].rank(method="min", ascending=False).astype(int)

df.to_csv("ranked_students.csv", index=False)


