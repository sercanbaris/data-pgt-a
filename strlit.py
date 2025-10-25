import streamlit as st
import plotly.express as px
import pandas as pd

# Page configuration
st.set_page_config(page_title="PGT-A Analysis Dashboard", layout="wide", page_icon="🔬")

# Load data
@st.cache_data
def load_data():
    return pd.read_excel('pre_analysis_last.xlsx')

data = load_data()

# Title and description
st.title("🔬 PGT-A Analysis Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

# Hospital location filter
location_filter = st.sidebar.multiselect(
    "Select Hospital Location",
    options=sorted(data['hospital_location'].unique()),
    default=sorted(data['hospital_location'].unique())
)

# Hospital filter
hospital_filter = st.sidebar.multiselect(
    "Select Hospital",
    options=sorted(data['Hospital'].unique()),
    default=sorted(data['Hospital'].unique())
)

# Filter data
filtered_data = data[
    (data['hospital_location'].isin(location_filter)) &
    (data['Hospital'].isin(hospital_filter))
]

filtered_data = filtered_data.reset_index(drop=True)


# Main metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Hospitals", len(filtered_data['Hospital'].unique()))
with col2:
    st.metric("Total Embryos", f"{filtered_data['embryo_count'].sum():,.0f}")

with col3:
    st.metric("Avg CH-RATE", f"{filtered_data['CH-RATE'].mean():.2f}%")
with col4:
    st.metric("Avg AF-RATE", f"{filtered_data['AF-RATE'].mean():.2f}%")
with col5:
    st.metric("Avg IC-RATE", f"{filtered_data['IC-RATE'].mean():.2f}%")
with col6:
    st.metric("Total Patients", f"{filtered_data['patient_count'].sum():,.0f}")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Table", "📈 Visualizations", "🔍 Statistics", "📥 Download"])

with tab1:
    st.subheader("Data Table")
    
    # Search functionality
    search = st.text_input("🔍 Search in table", "")
    if search:
        mask = filtered_data.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        display_data = filtered_data[mask]
    else:
        display_data = filtered_data
    
    # Display dataframe with formatting
    st.dataframe(
        display_data.style.format({
            'embryo_count': '{:,.0f}',
            'CH-RATE': '{:.2f}',
            'AF-RATE': '{:.2f}',
            'IC-RATE': '{:.2f}'
        }).background_gradient(subset=['CH-RATE', 'AF-RATE', 'IC-RATE'], cmap='RdYlGn'),
        height=500,
        use_container_width=True
    )
    
    st.info(f"Showing {len(display_data)} of {len(filtered_data)} records")

with tab2:
    st.subheader("Visualizations")
    
    # Chart type selector
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Scatter plot
        st.markdown("#### Embryo Count vs Rates")
        metric_choice = st.selectbox("Select Metric", ['CH-RATE', 'AF-RATE', 'IC-RATE'])
        
        fig_scatter = px.scatter(
            filtered_data,
            x='embryo_count',
            y=metric_choice,
            color='Hospital',
            size='embryo_count',
            hover_data=['Hospital', 'hospital_location'],
            title=f'{metric_choice} vs Embryo Count'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with chart_col2:
        # Bar chart
        st.markdown("#### Average Rates by Hospital")
        avg_data = filtered_data.groupby('Hospital')[['CH-RATE', 'AF-RATE', 'IC-RATE']].mean().reset_index()
        
        fig_bar = px.bar(
            avg_data,
            x='Hospital',
            y=[metric_choice],
            title=f'Average {metric_choice} by Hospital',
            color_discrete_sequence=['#FF6B6B']
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Box plot
    st.markdown("#### Distribution of Rates")
    fig_box = px.box(
        filtered_data,
        y=['CH-RATE', 'AF-RATE', 'IC-RATE'],
        title="Distribution of All Rates"
    )
    st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.subheader("Statistical Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Descriptive Statistics")
        st.dataframe(
            filtered_data[['embryo_count', 'CH-RATE', 'AF-RATE', 'IC-RATE']].describe(),
            use_container_width=True
        )
    
    with col2:
        st.markdown("#### Correlation Matrix")
        corr_data = filtered_data[['embryo_count', 'CH-RATE', 'AF-RATE', 'IC-RATE']].corr()
        fig_heatmap = px.imshow(
            corr_data,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title="Correlation Heatmap"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Group statistics
    st.markdown("#### Statistics by Hospital Location")
    location_stats = filtered_data.groupby('hospital_location').agg({
        'embryo_count': ['sum', 'mean'],
        'CH-RATE': 'mean',
        'AF-RATE': 'mean',
        'IC-RATE': 'mean'
    }).round(2)
    st.dataframe(location_stats, use_container_width=True)

with tab4:
    st.subheader("Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download filtered data as CSV
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name='filtered_pgt_data.csv',
            mime='text/csv',
        )
    
    with col2:
        # Download summary statistics
        summary = filtered_data.describe().to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Statistics (CSV)",
            data=summary,
            file_name='statistics.csv',
            mime='text/csv',
        )
    
    st.info("💡 Tip: Use filters in the sidebar to customize your data before downloading")

# Footer
st.markdown("---")
st.markdown("**PGT-A Analysis Dashboard** | Data visualization and analysis tool")