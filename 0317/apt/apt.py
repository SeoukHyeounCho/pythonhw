import pandas as pd
import matplotlib.pylab as plt
from statsmodels.formula.api import ols
from sklearn.linear_model import LinearRegression
price = [
    174000, 156500, 168000, 145000, 182000, 163000, 155500, 170000, 149000, 177500,
    165000, 140000, 148000, 159500, 152000, 132000, 120000, 180000, 142000, 135000,
    125000, 137000, 110000, 185000, 100000, 139500, 160500, 150000, 154000, 143000
]

size = [
    152, 118, 118, 85, 160, 130, 110, 143, 100, 158,
    120, 95, 128, 110, 105, 86, 76, 155, 115, 80,
    72, 140, 65, 162, 59, 128, 128, 115, 100, 123
]

age = [
    19, 19, 19, 19, 20, 18, 17, 19, 16, 20,
    15, 14, 20, 17, 19, 12, 12, 11, 11, 18,
    13, 14, 13, 12, 11, 11, 11, 11, 17, 16
]

kindergarten = [
    22, 22, 22, 22, 20, 18, 16, 19, 15, 14,
    12, 11, 10, 9, 8, 7, 6, 5, 5, 9,
    10, 5, 6, 7, 4, 4, 4, 4, 9, 8
]

elementarySchool = [
    10, 10, 10, 10, 9, 8, 10, 11, 9, 8,
    7, 10, 8, 8, 9, 11, 10, 9, 10, 9,
    8, 9, 11, 10, 12, 12, 12, 12, 10, 11
]

busStop = [
    13, 13, 13, 13, 15, 14, 17, 19, 20, 14,
    18, 22, 20, 16, 25, 27, 21, 23, 24, 16,
    28, 18, 23, 25, 29, 29, 29, 29, 27, 20
]

hospital = [
    19, 19, 19, 19, 18, 20, 17, 18, 16, 15,
    17, 16, 15, 14, 18, 20, 21, 22, 15, 16,
    14, 19, 15, 16, 14, 14, 14, 14, 18, 16
]

mart = [
    19, 19, 19, 19, 18, 20, 17, 18, 16, 15,
    17, 16, 15, 14, 18, 20, 21, 22, 15, 16,
    14, 19, 15, 16, 14, 14, 14, 14, 18, 16
]
data = {'price': price, 'size': size, 'age': age, 'kindergarten': 
kindergarten, 'elementarySchool': elementarySchool, 'busStop': busStop, 
'hospital': hospital, 'mart': mart}
df = pd.DataFrame(data)
fit = ols('price ~ size + age + kindergarten + elementarySchool + busStop + hospital + mart', data=df).fit( )
print(fit.summary( ))
