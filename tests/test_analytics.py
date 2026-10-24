
from services.analytics import execute_query

sql = """
SELECT product,
       SUM(quantity * unit_price - discount_amount) AS revenue
FROM sales
WHERE status = 'Completed'
  AND missing_price = 0
  AND invalid_numeric = 0
  AND invalid_date = 0
GROUP BY product
ORDER BY revenue DESC
LIMIT 5
"""

print(execute_query(sql))
