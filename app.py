"""
------------------------------------------------------------------------------
EDA on Suicidal Tendencies - Streamlit Dashboard
Author: Jaya (2025)
License: CC BY-NC-ND 4.0 International

This code is protected under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License.

You may:
- View and share the code with credit.
You may not:
- Use it commercially.
- Modify or redistribute modified versions.

See full license: https://creativecommons.org/licenses/by-nc-nd/4.0/

Contact: ojayashre@gmail.com
------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import base64
from datetime import datetime




def get_india_geojson():
    return "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson"

# Configure page
st.set_page_config(
    page_title="Suicide Analysis in India",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f5f5f5;}
    .stDownloadButton button {width: 100%;}
    .stSelectbox:first-child label {font-weight: bold;}
    div[data-testid="stExpander"] div[role="button"] p {font-size: 18px;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    # Convert columns to proper case for consistency
    df['State'] = df['State'].str.title()
    df['Type'] = df['Type'].str.title()
    df['Gender'] = df['Gender'].str.title()
    states_to_remove = ['Total (All India)','Total (States)', 'Total (Uts)' ]
    df = df[~df['State'].isin(states_to_remove)]

    return df

# Sidebar configuration
st.sidebar.header("⚙️ Dashboard Configuration")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if not uploaded_file:
    st.warning("Please upload a CSV file through the sidebar")
    st.stop()

df = load_data(uploaded_file)

# Customization options
st.sidebar.subheader("🎨 Visualization Settings")
theme = st.sidebar.selectbox("Choose Theme", ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"])
primary_color = st.sidebar.color_picker("Primary Color", "#1f77b4")
secondary_color = st.sidebar.color_picker("Secondary Color", "#ff7f0e")

# Filters
st.sidebar.subheader("🔍 Data Filters")
selected_states = st.sidebar.multiselect(
    "Select States",
    options=df['State'].unique(),
    default=df['State'].unique()
)

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(int(df['Year'].min()), int(df['Year'].max()))
)

selected_type = st.sidebar.multiselect(
    "Select Type",
    options=df['Type'].unique(),
    default=df['Type'].unique()
)

selected_gender = st.sidebar.multiselect(
    "Select Gender",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

selected_age_group = st.sidebar.multiselect(
    "Select Age Group",
    options=df['Age_group'].unique(),
    default=df['Age_group'].unique()
)

# Apply filters
filtered_df = df[
    (df['State'].isin(selected_states)) &
    (df['Year'].between(selected_years[0], selected_years[1])) &
    (df['Type'].isin(selected_type)) &
    (df['Gender'].isin(selected_gender)) &
    (df['Age_group'].isin(selected_age_group))
]

# Download functions
def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download CSV</a>'

def get_plot_download_link(fig, title):
    buffer = StringIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    html_bytes = buffer.getvalue().encode()
    b64 = base64.b64encode(html_bytes).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{title}.html">Download Chart</a>'

# Main dashboard
st.title("📈 Suicide Tendency Analysis in India")
st.markdown(f"### Custom Report Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Dashboard header with download options
col1, col2, col3 = st.columns([2,1,1])
with col2:
    st.markdown(get_csv_download_link(filtered_df), unsafe_allow_html=True)
with col3:
    if st.button("Generate PDF Report"):
        st.warning("PDF generation feature requires additional setup")

# Key Metrics
st.subheader("🔑 Key Statistics")
metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("Total Cases", f"{filtered_df['Total'].sum():,}", help="Total cases in selected filters")
with metric_cols[1]:
    st.metric("Avg Annual Cases", f"{filtered_df.groupby('Year')['Total'].mean().mean():,.0f}")
with metric_cols[2]:
    st.metric("Most Affected State", filtered_df.groupby('State')['Total'].sum().idxmax())
with metric_cols[3]:
    st.metric("Gender Ratio", f"{filtered_df[filtered_df['Gender']=='Male']['Total'].sum()/filtered_df['Total'].sum()*100:.1f}% Male")

# Visualizations
st.markdown("---")
st.header("📊 Data Visualizations")

# Visualization 1 - Trend Over Years
with st.expander("📈 Annual Trend Analysis", expanded=True):
    col1, col2 = st.columns([4,1])
    with col1:
        yearly_data = filtered_df.groupby('Year')['Total'].sum().reset_index()
        fig = px.line(yearly_data, x='Year', y='Total', 
                     title="Yearly Trend of Cases",
                     color_discrete_sequence=[primary_color])
        fig.update_layout(template=theme)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown(get_plot_download_link(fig, "Annual_Trend"), unsafe_allow_html=True)
        st.dataframe(yearly_data.set_index('Year'))

# Visualization 2 - Demographic Analysis
with st.expander("👥 Demographic Breakdown"):
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("Analysis Category", ['Type', 'Gender', 'Age_group'])
        category_data = filtered_df.groupby(category)['Total'].sum().reset_index()
        fig = px.pie(category_data, names=category, values='Total',
                    title=f"Distribution by {category}",
                    color_discrete_sequence=[primary_color, secondary_color])
        fig.update_layout(template=theme)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(get_plot_download_link(fig, f"Distribution_{category}"), unsafe_allow_html=True)
    
    with col2:
        state_data = filtered_df.groupby('State')['Total'].sum().reset_index().sort_values('Total', ascending=False)
        fig = px.bar(state_data, x='State', y='Total',
                    title="State-wise Distribution",
                    color='Total', color_continuous_scale=[primary_color, secondary_color])
        fig.update_layout(template=theme, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(get_plot_download_link(fig, "State_Distribution"), unsafe_allow_html=True)

# Visualization 3 - Advanced Analysis
with st.expander("🔍 Advanced Analysis"):
    analysis_type = st.selectbox("Select Analysis Type", 
                               ["Age Group Trends", "Gender Comparison", "Type Distribution"])
    
    if analysis_type == "Age Group Trends":
        data = filtered_df.groupby(['Year', 'Age_group'])['Total'].sum().reset_index()
        fig = px.area(data, x='Year', y='Total', color='Age_group',
                      title="Age Group Trends Over Time",
                      color_discrete_sequence=px.colors.qualitative.Plotly)
    elif analysis_type == "Gender Comparison":
        data = filtered_df.groupby(['Year', 'Gender'])['Total'].sum().reset_index()
        fig = px.bar(data, x='Year', y='Total', color='Gender',
                    title="Gender Comparison Over Time",
                    barmode='group', 
                    color_discrete_sequence=[primary_color, secondary_color])
    else:
        data = filtered_df.groupby(['Year', 'Type'])['Total'].sum().reset_index()
        fig = px.scatter(data, x='Year', y='Total', color='Type',
                        size='Total', hover_name='Type',
                        title="Type Distribution Over Time",
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    
    fig.update_layout(template=theme)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(get_plot_download_link(fig, analysis_type.replace(" ", "_")), unsafe_allow_html=True)

with st.expander("🗺️ State-wise Heatmap"):
    st.markdown("### Geographical Distribution of Cases")
    
    # Aggregate data for map
    map_data = filtered_df.groupby('State')['Total'].sum().reset_index()
    
    state_name_mapping = {
        'Odisha': 'Orissa',
        "Jammu & Kashmir" : "Jammu and Kashmir",
        "A & N Islands" : "Andaman and Nicobar",
        "D & N Haveli" : "Dadra and Nagar Haveli",
        "Daman & Diu"  : "Daman and Diu",
        "Delhi (Ut)" : "Delhi",
        "Uttarakhand" : "Uttaranchal"
    }
    map_data['State'] = map_data['State'].replace(state_name_mapping)

    
    # Create choropleth map
    fig = px.choropleth(
        map_data,
        geojson=get_india_geojson(),
        locations='State',
        featureidkey= "properties.NAME_1",
        color='Total',
        color_continuous_scale=st.session_state.get('color_scale', 'Viridis'),
        range_color=(0, map_data['Total'].max()),
        scope='asia',
        labels={'Total': 'Total Cases'},
        hover_data=['State', 'Total']
    )
    
    # Update map layout
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600,
        coloraxis_colorbar=dict(
            title="Total Cases",
            thickness=20,
            len=0.75
        )
    )
    
    # Add map controls
    col1, col2 = st.columns([4,1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.selectbox(
            "Color Scale",
            options=['Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis'],
            key='color_scale'
        )
        st.markdown(get_plot_download_link(fig, "India_Heatmap"), unsafe_allow_html=True)
        st.markdown("""
            **Map Notes:**
            - Hover over states to see exact numbers
            - Color intensity represents total cases
            - Unavailable data shown in gray
        """)

# Footer
st.markdown("---")

