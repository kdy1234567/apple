"""
Streamlit app: MBTI Most-Common Type by Country (demo + scraper fallback)
- Shows a world choropleth where each country is colored by its most-common MBTI type (categorical)
- Requires a CSV `mbti_by_country.csv` with columns: country, iso_alpha3, top_type, percentage

Notes:
- 16Personalities provides country profiles based on >40M respondents (use for scraping if desired). See: https://16personalities.com (included in README).
- Many country pages are JS-driven; scraping may fail. This app includes a best-effort scraper but provides a sample CSV fallback for demonstration.

To run locally:
1. pip install -r requirements.txt
2. streamlit run streamlit-mbti-country-map.py

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry
import requests
from bs4 import BeautifulSoup
from functools import lru_cache
import io

st.set_page_config(layout="wide", page_title="MBTI by Country — Map")

st.title("MBTI: Most-common Personality Type by Country")
st.markdown(
    """\
This demo shows, for each country, which MBTI type is most common and its percentage. 

**Important:** Public datasets on country-level MBTI are limited and often come from self-selected online test takers (e.g. 16Personalities). The app includes a small sample CSV for demonstration and a best-effort scraper for 16Personalities country pages — scraping may fail because those pages are JS-driven.
"""
)

# ------------------------------
# Utility functions
# ------------------------------

def country_to_iso3(name):
    try:
        country = pycountry.countries.lookup(name)
        return country.alpha_3
    except Exception:
        # manual overrides for common mismatches
        overrides = {
            'United States': 'USA',
            'South Korea': 'KOR',
            'North Korea': 'PRK',
            'Russia': 'RUS',
            'Czech Republic': 'CZE',
            'Iran': 'IRN',
            'Syria': 'SYR',
            'Venezuela': 'VEN',
            'Bolivia': 'BOL',
            'Vietnam': 'VNM',
            'Tanzania': 'TZA',
            'Laos': 'LAO',
        }
        return overrides.get(name)


@st.cache_data(show_spinner=False)
def load_sample_data():
    # small sample dataset included inline for immediate demo
    csv = io.StringIO(
"""
country,iso_alpha3,top_type,percentage
United States,USA,ISTJ,12.3
South Korea,KOR,ISFJ,10.1
Japan,JPN,ISTJ,11.0
United Kingdom,GBR,ISFJ,12.0
Germany,DEU,ISTJ,11.5
Brazil,BRA,ESFP,9.0
India,IND,ISTJ,10.5
Australia,AUS,ISFJ,10.8
Canada,CAN,ISFJ,11.2
France,FRA,ISFJ,9.8
"""
    )
    return pd.read_csv(csv)


# Best-effort scraper for 16personalities country pages (may not work if site requires JS)
@lru_cache(maxsize=1)
def scrape_16personalities_world():
    """Try to gather country -> top MBTI + percentage from 16personalities country profiles.
    Returns a DataFrame or raises an exception if scraping clearly failed.
    """
    base = 'https://www.16personalities.com'
    world_url = base + '/country-profiles/global/world'
    headers = { 'User-Agent': 'mbti-country-map-bot/1.0 (demo)' }
    resp = requests.get(world_url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch world page: {resp.status_code}")

    soup = BeautifulSoup(resp.text, 'html.parser')
    # Attempt: find links to country profiles
    links = []
    for a in soup.select('a'):
        href = a.get('href', '')
        if href.startswith('/country-profiles/') and href.count('/') >= 2:
            full = base + href
            if full not in links:
                links.append(full)

    results = []
    for url in links:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                continue
            s = BeautifulSoup(r.text, 'html.parser')
            # heuristic: look for 'Top personality types' area — try to find percentage numbers in page text
            text = s.get_text(separator=' ')
            # naive extraction: find occurrences like 'ISTJ' near a '%' sign
            import re
            m = re.search(r'([A-Z]{4})[^%\n]{0,40}([0-9]{1,2}\.[0-9]|[0-9]{1,2})%', text)
            if m:
                ttype = m.group(1)
                perc = float(m.group(2))
            else:
                # fallback: pick first type word from a known list and try to find percentage
                types = ['ISTJ','ISFJ','INFJ','INTJ','ISTP','ISFP','INFP','INTP','ESTP','ESFP','ENFP','ENTP','ESTJ','ESFJ','ENFJ','ENTJ']
                found_type = None
                for tt in types:
                    if tt in text:
                        found_type = tt
                        break
                if not found_type:
                    continue
                # find nearest percentage
                idx = text.find(found_type)
                nearby = text[max(0, idx-80): idx+80]
                m2 = re.search(r'([0-9]{1,2}\.[0-9]|[0-9]{1,2})%', nearby)
                if m2:
                    perc = float(m2.group(1))
                else:
                    perc = None
                ttype = found_type

            # guess country name from URL
            country_slug = url.rstrip('/').split('/')[-1].replace('-', ' ').title()
            iso = country_to_iso3(country_slug)
            results.append({'country': country_slug, 'iso_alpha3': iso, 'top_type': ttype, 'percentage': perc})
        except Exception:
            continue

    if not results:
        raise RuntimeError('No results scraped — site may be JS-driven or blocking requests')

    df = pd.DataFrame(results)
    return df


# ------------------------------
# UI: data source choice
# ------------------------------

st.sidebar.header('Data')
data_option = st.sidebar.selectbox('Choose data source', ['Demo sample CSV (recommended for quick start)', 'Try scrape 16Personalities (best-effort)'])

if data_option.startswith('Demo'):
    df = load_sample_data()
else:
    with st.spinner('Attempting to scrape 16Personalities (may fail)...'):
        try:
            df = scrape_16personalities_world()
            st.success('Scrape successful — showing scraped results')
        except Exception as e:
            st.error('Scraping failed: ' + str(e))
            st.info('Falling back to demo sample data')
            df = load_sample_data()

# ensure iso column
if 'iso_alpha3' not in df.columns:
    df['iso_alpha3'] = df['country'].apply(country_to_iso3)

# drop rows without iso
df_display = df.dropna(subset=['iso_alpha3']).copy()

# color map: map MBTI types to numeric categories for consistent coloring
mbti_types = sorted(df_display['top_type'].unique())
mapping = {t:i for i,t in enumerate(mbti_types)}
df_display['type_id'] = df_display['top_type'].map(mapping)

fig = px.choropleth(df_display,
                    locations='iso_alpha3',
                    color='top_type',
                    hover_name='country',
                    hover_data=['top_type','percentage'],
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    category_orders={ 'top_type': mbti_types },
                    projection='natural earth')
fig.update_layout(margin=dict(l=0,r=0,t=30,b=0))

st.plotly_chart(fig, use_container_width=True)

# show table
with st.expander('Raw data (preview)'):
    st.dataframe(df_display[['country','iso_alpha3','top_type','percentage']])

st.markdown('---')
st.markdown('**Sources & notes**')
st.markdown('- 16Personalities country profiles (aggregated user responses; sample sizes vary; self-selected online testers). See their Country Profiles pages.')
st.markdown('- This app is a demo. Country-level MBTI statistics are noisy and sampled from online test-takers; interpret with caution.')

st.markdown('**Next steps / improvements**')
st.markdown('- Replace demo CSV with a validated dataset (CSV/JSON) covering the countries you want.')
st.markdown('- If you want, I can prepare a GitHub repo with this app, requirements.txt and an example CSV ready to push and deploy to Streamlit Community Cloud.')


