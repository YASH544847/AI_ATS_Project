import joblib

le_company = joblib.load("le_company.pkl")

print(le_company.classes_)