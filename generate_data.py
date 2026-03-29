import pandas as pd
import numpy as np

np.random.seed(42)

N = 350  # more than required 300

sectors = ["Manufacturing", "IT", "Retail", "Food", "Textile"]
locations = ["Urban", "Semi-Urban", "Rural"]
categories = ["Micro", "Small", "Medium"]

data = []

for i in range(N):

    revenue = np.random.randint(5, 120) * 100000
    growth_rate = np.random.uniform(0.02, 0.25)
    profit_margin = np.random.uniform(5, 30)
    debt = np.random.randint(1, 50) * 100000
    employees = np.random.randint(5, 250)
    tech_level = np.random.randint(1, 6)
    gst_score = np.random.randint(40, 100)

    # Logical Growth Score Calculation
    score = (
        growth_rate * 100
        + profit_margin
        + tech_level * 5
        + gst_score * 0.3
    )

    if score > 95:
        growth = "High"
    elif score > 70:
        growth = "Moderate"
    else:
        growth = "Low"

    data.append({
        "MSME_ID": i,
        "Sector": np.random.choice(sectors),
        "Years_of_Operation": np.random.randint(1, 20),
        "Category": np.random.choice(categories),
        "Location_Type": np.random.choice(locations),
        "Annual_Revenue": revenue,
        "Revenue_Growth_Rate": growth_rate,
        "Profit_Margin": profit_margin,
        "Debt_Outstanding": debt,
        "Loan_to_Revenue_Ratio": debt / revenue,
        "Number_of_Employees": employees,
        "Technology_Level": tech_level,
        "GST_Compliance_Score": gst_score,
        "Growth_Category": growth
    })

df = pd.DataFrame(data)
df.to_csv("msme_data.csv", index=False)

print("MSME dataset generated successfully!")