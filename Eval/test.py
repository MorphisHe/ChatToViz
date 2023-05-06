import matplotlib.pyplot as plt

teststring = """

import pandas as pd
import matplotlib.pyplot as plt

data = {'Document_ID': [7, 11, 81, 81, 81, 111, 119, 166, 166, 170, 230, 230,
                         252, 252, 260],
        'Location_Code': ['e', 'x', 'c', 'c', 'x', 'x', 'b', 'b', 'b', 'x', 'e',
                          'e', 'n', 'x', 'e'],
        'Date_in_Location_From': ['2017-01-06 23:17:22', '2017-01-06 23:17:22',
                                   '1972-03-31 09:47:22', '2017-01-06 23:17:22',
                                   '2008-06-08 12:45:38', '1986-10-14 17:53:39',
                                   '2017-01-06 23:17:22', '1985-05-13 12:19:43',
                                   '1986-10-14 17:53:39', '1997-03-10 15:24:00',
                                   '1972-03-31 09:47:22', '2010-11-26 19:22:50',
                                   '2017-01-06 23:17:22', '1972-03-31 09:47:22',
                                   '2009-08-18 03:29:08'],
        'Date_in_Locaton_To': ['2008-06-08 12:45:38', '2012-07-03 09:48:46',
                               '1987-11-05 06:11:22', '2010-11-26 19:22:50',
                               '1976-06-15 03:40:06', '2010-11-26 19:22:50',
                               '1995-01-01 03:52:11', '1986-10-14 17:53:39',
                               '2010-11-26 19:22:50', '1976-06-15 03:40:06',
                               '1987-11-05 06:11:22', '2017-01-06 23:17:22',
                               '1997-03-10 15:24:00', '2009-08-18 03:29:08',
                               '1986-10-14 17:53:39']}

df = pd.DataFrame(data)

freq = df['Date_in_Location_From'].value_counts().sort_values(ascending=False)

plt.figure(figsize=(10,8))
plt.bar(freq.index, freq.values)
plt.xticks(rotation=90)
plt.xlabel('Date_in_Location_From')
plt.ylabel('Document Frequency')
plt.title('Bar chart of Date_in_Location_From column')
plt.show()
"""
if __name__==   "__main__":
    exec(teststring)
    plt.savefig('plot.png')