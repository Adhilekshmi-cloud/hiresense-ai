import pandas as pd

schemes = [
    {
        "Scheme_ID": 1,
        "Scheme_Name": "Tech Modernization Scheme",
        "Eligible_Sectors": "Manufacturing,IT",
        "Max_Subsidy_Amount": 500000,
        "Impact_Factor_Revenue": 20,
        "Impact_Factor_Employment": 5
    },
    {
        "Scheme_ID": 2,
        "Scheme_Name": "Rural Development Boost",
        "Eligible_Sectors": "Food,Textile",
        "Max_Subsidy_Amount": 300000,
        "Impact_Factor_Revenue": 15,
        "Impact_Factor_Employment": 8
    },
    {
        "Scheme_ID": 3,
        "Scheme_Name": "Export Promotion Incentive",
        "Eligible_Sectors": "Manufacturing,Textile",
        "Max_Subsidy_Amount": 400000,
        "Impact_Factor_Revenue": 25,
        "Impact_Factor_Employment": 4
    },
    {
        "Scheme_ID": 4,
        "Scheme_Name": "Digital Transformation Grant",
        "Eligible_Sectors": "IT,Retail",
        "Max_Subsidy_Amount": 350000,
        "Impact_Factor_Revenue": 18,
        "Impact_Factor_Employment": 6
    },
    {
        "Scheme_ID": 5,
        "Scheme_Name": "Employment Generation Scheme",
        "Eligible_Sectors": "All",
        "Max_Subsidy_Amount": 450000,
        "Impact_Factor_Revenue": 10,
        "Impact_Factor_Employment": 10
    }
]

df = pd.DataFrame(schemes)
df.to_csv("scheme_data.csv", index=False)

print("Scheme dataset generated successfully!")