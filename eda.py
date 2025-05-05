import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("ranked_students.csv")
top10 = df.sort_values("cur._cgpa", ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.barh(top10["name"], top10["cur._cgpa"])
plt.xlabel("CGPA")
plt.title("Top 10 Students by CGPA")
plt.gca().invert_yaxis()
plt.show()
