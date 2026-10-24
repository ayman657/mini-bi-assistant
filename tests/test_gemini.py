
from services.text_to_sql import generate_sql

question = "Which product generated the highest revenue?"

try:
    sql = generate_sql(question)
    print("\nGenerated SQL:\n")
    print(sql)

except Exception as exc:
    print("Error:", exc)
