# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Funding Rounds Analysis 2025")

# --------------------------
# Load Dataset
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("funding-rounds-cleaned.xlsx")
    df['organization_industries'] = df['organization_industries'].fillna('')
    df['investor_names'] = df['investor_names'].fillna('')
    return df

df = load_data()

# --------------------------
# Preprocessing
# --------------------------
df_industry = df.assign(
    organization_industries=df['organization_industries'].str.split(', ')
).explode('organization_industries')

df_investor = df_industry.assign(
    investor_names=df_industry['investor_names'].str.split(', ')
).explode('investor_names')


# --------------------------
# Streamlit App Layout
# --------------------------

st.title("🚀 Startup Funding Rounds Analysis 2025")
st.markdown("Interactive visualization of deals, funding, and investor activity by industry.")


# --------------------------
# Task 1: Number of Deals by Industry
# --------------------------
st.header("1️. Number of Deals by Industry")

deals_by_industry = df_industry[df_industry['organization_industries'] != ""].groupby('organization_industries')['organization_name'].count().sort_values(ascending=False).head(10)

fig1 = px.bar(
    deals_by_industry,
    x=deals_by_industry.index,
    y=deals_by_industry.values,
    color=deals_by_industry.values,
    color_continuous_scale='Viridis',
    text=deals_by_industry.values,
    title='Number of Deals by Industry (Top 10, 2025)'
)
fig1.update_traces(textposition='outside')
fig1.update_layout(xaxis_title='Industry', yaxis_title='Number of Deals', xaxis_tickangle=-45, coloraxis_showscale=False, width=1000, height=600)
st.plotly_chart(fig1)

st.markdown("""
**Insights**
- Artificial Intelligence (AI) leads by a wide margin (~446 deals).
- Software (~351 deals) is the second strongest sector.
- SaaS (179) and Information Technology (166) form a strong second tier.
- Traditional sectors like Manufacturing (48) and FinTech (45) are lower in deal count.
- AI dominates deal activity; investors favor scalable software-driven businesses.
""")


# --------------------------
# Task 2: Money Invested by Industry
# --------------------------
st.header("2️. Money Invested by Industry")

funding_by_industry = (
    df_industry
    .groupby('organization_industries')['money_raised_(in_usd)']
    .sum()
    .reset_index()
    .sort_values(by='money_raised_(in_usd)', ascending=False)
)

TOP_N = 80
top_industries = funding_by_industry.head(TOP_N)
other_industries = funding_by_industry.iloc[TOP_N:]
other_row = pd.DataFrame({
    'organization_industries': ['Other'],
    'money_raised_(in_usd)': [other_industries['money_raised_(in_usd)'].sum()]
})
funding_treemap_df = pd.concat([top_industries, other_row], ignore_index=True)

fig2 = px.treemap(
    funding_treemap_df,
    path=['organization_industries'],
    values='money_raised_(in_usd)',
    color='money_raised_(in_usd)',
    color_continuous_scale='Blues',
    title='Money Invested by Industry (Top 20 + Other, 2025)',
    hover_data={'money_raised_(in_usd)':':$,.0f'}
)
fig2.update_traces(textinfo="label+value")
fig2.update_layout(width=1000, height=700)
st.plotly_chart(fig2)

st.markdown("""
**Insights**
- AI: ~$369M, largest single block; “Other”: ~$346M, indicating long-tail diversification.
- Software: ~$244M, Information Technology: ~$191M, Generative AI: ~$93M, SaaS: ~$78M.
- AI dominates both volume and capital; capital spreads into emerging niches.
- Generative AI raises large amounts per deal, reflecting high investor conviction.
""")


# --------------------------
# Task 3: Industry-wise Deals by Top 5 Investors
# --------------------------
st.header("3️. Industry-wise Deals by Top 5 Investors")

df_exp = df.assign(
    organization_industries=df['organization_industries'].str.split(', '),
    investor_names=df['investor_names']
        .fillna('')
        .replace('Not Mentioned', '')
        .str.split(', ')
).explode('organization_industries').explode('investor_names')
df_exp = df_exp[df_exp['investor_names'].str.strip() != '']

TOP_INVESTORS = 5
top_investors = (
    df_exp
    .groupby('investor_names')['organization_name']
    .nunique()
    .sort_values(ascending=False)
    .head(TOP_INVESTORS)
    .index
)

df_top_inv = df_exp[df_exp['investor_names'].isin(top_investors)]
TOP_INDUSTRIES = 10
top_industries = (
    df_exp
    .groupby('organization_industries')['organization_name']
    .nunique()
    .sort_values(ascending=False)
    .head(TOP_INDUSTRIES)
    .index
)
df_top = df_top_inv[df_top_inv['organization_industries'].isin(top_industries)]

inv_ind_deals = (
    df_top
    .groupby(['investor_names', 'organization_industries'])
    .nunique()['organization_name']
    .reset_index(name='deal_count')
)

fig3 = px.bar(
    inv_ind_deals,
    x='investor_names',
    y='deal_count',
    color='organization_industries',
    barmode='group',
    text='deal_count',
    title='Industry-wise Deal Distribution for Top 5 Investors (2025)'
)
fig3.update_traces(textposition='outside')
fig3.update_layout(width=1600, height=900, xaxis_title='Investor', yaxis_title='Number of Deals', legend_title='Industry', title={'x':0.5}, bargap=0.25, bargroupgap=0.1)
st.plotly_chart(fig3)

st.markdown("""
**Insights**
- Y Combinator dominates deal count across almost all industries, especially AI, Software, SaaS, IT.
- Techstars is diversified at lower scale; Plug and Play is more selective.
- Pioneer Fund & Team Ignite focus on early-stage AI + Software.
- AI is the common overlap sector for all top investors.
""")


# --------------------------
# Task 4: Money Invested by Top 5 Investors across Industries
# --------------------------
st.header("4️. Money Invested by Top 5 Investors")

df_money = df_exp.copy()
df_money['money_per_investor'] = df_money['money_raised_(in_usd)'] / df_money['investor_count_computed'].replace(0, 1)
df_money = df_money[(df_money['investor_names'].isin(top_investors)) & (df_money['organization_industries'].isin(top_industries))]

inv_ind_money = (
    df_money
    .groupby(['investor_names', 'organization_industries'])['money_per_investor']
    .sum()
    .reset_index()
)

fig4 = px.bar(
    inv_ind_money,
    x='investor_names',
    y='money_per_investor',
    color='organization_industries',
    barmode='group',
    text_auto=':.2s',
    title='Money Invested by Top 5 Investors across Top 10 Industries (2025)'
)
fig4.update_layout(width=1600, height=900, xaxis_title='Investor', yaxis_title='Money Invested (USD)', legend_title='Industry', title={'x':0.5}, bargap=0.25, bargroupgap=0.1, yaxis_tickprefix='$')
st.plotly_chart(fig4)

st.markdown("""
**Insights**
- YC deploys ~$200M+, 2–3x more than the other four combined.
- YC leads in AI (~$69M) and Generative AI (~$52M), diversifying broadly.
- Overall AI dominance persists even with YC's broad portfolio.
""")


# --------------------------
# Task 5: Money Invested by Top Investors (Excluding Y Combinator)
# --------------------------
st.header("5️. Top Investors (Excluding YC)")

EXCLUDED_INVESTORS = ['Y Combinator']
df_money_filtered = df_money[~df_money['investor_names'].isin(EXCLUDED_INVESTORS)]

top_investors_no_yc = (
    df_money_filtered
    .groupby('investor_names')['organization_name']
    .nunique()
    .sort_values(ascending=False)
    .head(TOP_INVESTORS)
    .index
)

df_money_filtered = df_money_filtered[df_money_filtered['investor_names'].isin(top_investors_no_yc)]

inv_ind_money_no_yc = (
    df_money_filtered
    .groupby(['investor_names', 'organization_industries'])['money_per_investor']
    .sum()
    .reset_index()
)

fig5 = px.bar(
    inv_ind_money_no_yc,
    x='investor_names',
    y='money_per_investor',
    color='organization_industries',
    barmode='group',
    text_auto=':.2s',
    title='Money Invested by Top Investors across Industries (Excluding Y Combinator, 2025)'
)
fig5.update_layout(width=1600, height=900, xaxis_title='Investor', yaxis_title='Money Invested (USD)', legend_title='Industry', title={'x':0.5}, bargap=0.25, bargroupgap=0.1, yaxis_tickprefix='$')
st.plotly_chart(fig5)

st.markdown("""
**Insights**
- Pioneer Fund leads (~$82–85M), far ahead of peers.
- AI captures 80–90% of capital from Pioneer and Team Ignite, showing strong sector focus.
- Smaller investors (Plug and Play, Techstars) are diversified but deploy much less.
- AI boom is broad-based, not just YC-driven.
""")


# Task 6: Average Pre-Seed Funding per Deal by Industry
# --------------------------
st.header("6️. Average Pre-Seed Funding per Deal by Industry")

TOP_INDUSTRIES = 10

top_industries = (
    df_industry[df_industry['organization_industries'] != '']
    .groupby('organization_industries')['organization_name']
    .nunique()
    .sort_values(ascending=False)
    .head(TOP_INDUSTRIES)
    .index
)

df_top_ind = df_industry[df_industry['organization_industries'].isin(top_industries)]

avg_funding_industry = (
    df_top_ind
    .groupby('organization_industries')['money_raised_(in_usd)']
    .mean()
    .reset_index()
    .sort_values(by='money_raised_(in_usd)', ascending=False)
)

fig6 = px.bar(
    avg_funding_industry,
    x='organization_industries',
    y='money_raised_(in_usd)',
    color='money_raised_(in_usd)',
    color_continuous_scale='Viridis',
    text_auto=':.2s',
    title='Average Pre-Seed Funding per Deal by Industry (Top 10, 2025)'
)

fig6.update_layout(
    width=1600,
    height=900,
    xaxis_title='Industry',
    yaxis_title='Average Money Raised (USD)',
    xaxis_tickangle=-45,
    title={'x': 0.5},
    coloraxis_showscale=False,
    yaxis_tickprefix='$'
)

st.plotly_chart(fig6)

st.markdown("""
**Insights**
- Generative AI tops at ~$1.37M per deal, nearly 4x B2B (~$354K).
- High averages in GenAI and Information Technology reflect premium valuations.
- Manufacturing ranks high (~$923K), likely due to capital needs.
- SaaS, B2B, and Health Care have lower averages, indicating tighter discipline.
- Capital is polarizing toward "hot" technical sectors early on.
""")
