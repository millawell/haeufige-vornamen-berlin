from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

plt.style.use('ggplot')
from matplotlib import cm
cm = cm.get_cmap('Dark2', 12).colors[1:]

@st.cache
def get_names():

    p = Path(".")   
    recs = []  

    for dir_ in p.iterdir():
        if dir_.is_dir() and not str(dir_).startswith("."):
            for file_ in dir_.iterdir():
                if file_.suffix == '.csv':
                    sub_df = pd.read_csv(file_)
                    sub_df['year'] = int(str(dir_))
                    sub_df['area'] = file_.stem
                    recs.append(sub_df)


    return pd.concat(recs)


names = get_names()

gender = st.sidebar.multiselect(
    'Gender',
    sorted(names.geschlecht.unique().tolist())
)
gender_filter = names.geschlecht.isin(gender) if len(gender)>0 else [True]*len(names)
st.sidebar.text(f"matching {np.array(gender_filter).sum()}/{len(names)}")

years = sorted(names.year.unique().tolist())
year = st.sidebar.multiselect('Year', years)

year_filter = names.year.isin(year) if len(year)>0 else [True]*len(names)
st.sidebar.text(f"matching {np.array(year_filter).sum()}/{len(names)}")

areas = sorted(names.area.unique().tolist())
area = st.sidebar.multiselect(
    'Area',
    areas
)
area_filter = names.area.isin(area) if len(area)>0 else [True]*len(names)
st.sidebar.text(f"matching {np.array(area_filter).sum()}/{len(names)}")


filtered = names[np.logical_and.reduce([
    gender_filter,
    year_filter,
    area_filter
])]

st.write("""# Names in Berlin """)

view = filtered.groupby('vorname').sum().sort_values('anzahl',ascending=False)

view.reset_index(level=0, inplace=True)
st.write(
    view[['vorname', 'anzahl']]
)

name = st.text_input('Search for name in your current selection', '')

found_names = view[view.vorname==name]
found_names_in_all = names[names.vorname==name]


if len(found_names)==1:
    
    found_name = found_names.iloc[0].vorname
    found_cnt = found_names.anzahl.sum()
    view_cnts = sorted(view.groupby("vorname").sum().anzahl)[::-1]
    view_cnts_unique = sorted(view.groupby("vorname").sum().anzahl.unique())[::-1]
    st.write(f"""## You found one name: {found_name}! """)
    
    fig, ax = plt.subplots(figsize=(10,4))

    st.write(f"""It is on position {view_cnts_unique.index(found_cnt)+1} of {len(view_cnts_unique)}.""")
    n, _, _ = ax.hist(view_cnts,np.arange(0, max(view_cnts)+1, 10), color=cm[0])
    ax.vlines(found_cnt, 0, max(n),color=cm[1])
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_ylabel('Fequency')
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10,4))
    year_counts = found_names_in_all.groupby('year').sum().anzahl
    year_counts.plot(ax=ax,c=cm[0])
    for year_ in year:
        ax.plot(year_, year_counts[year_], 's', c=cm[1])

    ax.set_ylabel('Fequency')
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10,4))
    found_names_in_all.groupby('area').sum().anzahl.sort_index().plot(
        kind='bar',
        ax=ax,
        color=[cm[1] if area_ in area else cm[0] for area_ in areas]
    )

    ax.set_ylabel('Fequency')
    st.pyplot(fig)

st.write("""
This app is dedicated to Malte ;). 

Die Daten sind lizenziert unter CC BY 3.0 DE (Creative Commons Namensnennung 3.0 Deutschland Lizenz).

Urheber: Berliner Landesamt für Bürger- und Ordnungsangelegenheiten (LABO) / BerlinOnline Stadtportal GmbH & Co. KG.

Zu finden unter: https://github.com/berlinonline/haeufige-vornamen-berlin

""")