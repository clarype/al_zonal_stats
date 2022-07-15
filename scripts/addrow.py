

import pandas as pd


dict = {'Name': ['Martha', 'Tim', 'Rob', 'Georgia'],
        'Maths': [87, 91, 97, 95],
        'Science': [83, 99, 84, 76]
        }

df = pd.DataFrame(dict)

print(df)
width = df.shape[1]
inpu = list(range(0,width))
df.loc[len(df.index)] = inpu

print(df)
print(df.iloc[-1][0])