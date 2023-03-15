import pandas as pd # library for data analysis
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML documents

from pprint import pprint as pp
import circlify as circ # library to handle circle packing
import matplotlib.pyplot as plt # library to handle visualization

# get the response in the form of html
wikiurl="https://en.wikipedia.org/wiki/List_of_largest_U.S._bank_failures"
response=requests.get(wikiurl)

# parse data from the html into a beautifulsoup object
soup = BeautifulSoup(response.text, 'html.parser')
banktable=soup.find('table',{'class':"wikitable"})

df=pd.read_html(str(banktable))
# convert list to dataframe
df=pd.DataFrame(df[0])

# data cleaning
def str_to_num(x):
    return float(x[1:len(x) - 8])

data = df.drop(["City", "State", "Ref."], axis=1)
data = data.rename(columns={
    "Assets at time of failure (nominal)": "Nominal Assets",
    "Assets at time of failure (inflation-adjusted, 2021)": "Adjusted Assets"
})
# quick data cleaning for new entry
data.at[91, 'Nominal Assets'] = '$3.8 billion'
data.at[91, 'Adjusted Assets'] = '$3.8 billion'
# 
data['Nominal Assets'] = data['Nominal Assets'].apply(str_to_num)
data['Adjusted Assets'] = data['Adjusted Assets'].apply(str_to_num)
data = data.sort_values(by=["Adjusted Assets"])

# circlifying data
col_list = list(data["Adjusted Assets"])
circles = circles = circ.circlify(
    col_list, 
    show_enclosure=False,
    target_enclosure=circ.Circle(x=0, y=0, r=200)
)
x_s = list(map(lambda x: x.x, circles))
y_s = list(map(lambda x: x.y, circles))
r_s = list(map(lambda x: x.r, circles))
data['x'] = x_s
data['y'] = y_s
data['r'] = r_s

# plotting the data
fig, ax = plt.subplots(figsize = (20, 20))
ax.axis('off')
plt.title('American Bank Failures Throughout History', fontsize = 30)

lim = max(
    max(
        abs(circle.x) + circle.r,
        abs(circle.y) + circle.r
    )
    for circle in circles
)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

def name_split(x):
    # Annoying long name cleaning
    if x == 'First National Bank, also operating as The National Bank of El Paso':
        x = 'The National Bank of El Paso'
    tokens = x.split()
    parity = True
    name = ''
    for token in tokens:
        name = f'{name}{token} ' if parity else f'{name}{token}\n'
        parity = not parity
    return name.rstrip()

labels = [f'{name_split(row[0])}\n{row[1]}\n${row[2]} billion' for row in zip(data['Bank'], data['Year'], data['Adjusted Assets'])]
years = list(data['Year'])

for circle, label, year in zip(circles, labels, years):
    x, y, r = circle
    ax.add_patch(plt.Circle((x, y), r, alpha=0.2, linewidth=2, facecolor='blue' if year != 2023 else 'red'))
    ax.annotate(
        label,
        (x, y),
        fontsize=r/4 if r < 5 else r/3,
        va='center',
        ha='center'
    )

plt.savefig('bank_failure.png', dpi=300)
plt.show()
