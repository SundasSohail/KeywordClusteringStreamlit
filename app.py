import streamlit as st
import pandas as pd
import json
from collections import defaultdict

def cluster_keywords_simple(keywords, categories):
    """Cluster keywords using simple word matching"""
    clusters = defaultdict(list)
    uncategorized = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        assigned = False
        
        for category in categories:
            category_lower = category.lower()
            # Split category into words
            category_words = category_lower.split()
            
            # Check if any word from category appears in keyword
            for word in category_words:
                if word in keyword_lower:
                    clusters[category].append(keyword)
                    assigned = True
                    break
            
            if assigned:
                break
        
        if not assigned:
            uncategorized.append(keyword)
    
    return clusters, uncategorized

# Page config
st.set_page_config(page_title="Keyword Clustering Tool", layout="wide", initial_sidebar_state="expanded")

# Title
st.title("🎯 Keyword Clustering Tool")
st.markdown("Upload your keywords and categories. Keywords will be organized into baskets based on word matching.")

# Sidebar
with st.sidebar:
    st.header("📁 Upload Files")
    
    keywords_file = st.file_uploader("Upload Keywords CSV", type=['csv'])
    categories_file = st.file_uploader("Upload Categories CSV", type=['csv'])
    
    st.markdown("---")
    st.subheader("📋 Sample Format")
    
    st.markdown("**Keywords CSV:**")
    st.code("""Keyword
german lederhosen women
traditional dirndl
men's shirt
leather belt""")
    
    st.markdown("**Categories CSV:**")
    st.code("""Category
Men Lederhosen & Outfits
Women Dirndl & Dresses
Men Shirts
Accessories""")

# Main content
if keywords_file and categories_file:
    try:
        # Load data
        keywords_df = pd.read_csv(keywords_file)
        categories_df = pd.read_csv(categories_file)
        
        # Validate columns
        if 'Keyword' not in keywords_df.columns:
            st.error("❌ Keywords CSV must have a 'Keyword' column")
            st.stop()
        
        if 'Category' not in categories_df.columns:
            st.error("❌ Categories CSV must have a 'Category' column")
            st.stop()
        
        keywords_list = keywords_df['Keyword'].dropna().tolist()
        categories_list = categories_df['Category'].dropna().tolist()
        
        if not keywords_list:
            st.error("❌ No keywords found in file")
            st.stop()
        
        if not categories_list:
            st.error("❌ No categories found in file")
            st.stop()
        
        # Cluster keywords
        clusters, uncategorized = cluster_keywords_simple(keywords_list, categories_list)
        
        st.success(f"✅ Processed {len(keywords_list)} keywords successfully!")
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Basket Summary", "Detailed View", "Download Results"])
        
        # Tab 1: Basket Summary
        with tab1:
            st.subheader("📊 Basket Summary")
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Keywords", len(keywords_list))
            with col2:
                st.metric("Categories", len(categories_list))
            with col3:
                assigned = len(keywords_list) - len(uncategorized)
                st.metric("Assigned", assigned)
            with col4:
                st.metric("Unassigned", len(uncategorized))
            
            st.markdown("---")
            
            # Basket summary table
            summary_data = []
            for category in categories_list:
                count = len(clusters.get(category, []))
                summary_data.append({"Basket Name": category, "Keywords Count": count})
            
            if uncategorized:
                summary_data.append({"Basket Name": "Other", "Keywords Count": len(uncategorized)})
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Tab 2: Detailed View
        with tab2:
            st.subheader("📝 Detailed View")
            
            for category in categories_list:
                if category in clusters and clusters[category]:
                    with st.expander(f"**{category}** ({len(clusters[category])} keywords)"):
                        for kw in clusters[category]:
                            st.write(f"• {kw}")
            
            if uncategorized:
                with st.expander(f"**Other** ({len(uncategorized)} keywords)"):
                    for kw in uncategorized:
                        st.write(f"• {kw}")
        
        # Tab 3: Download Results
        with tab3:
            st.subheader("📥 Download Results")
            
            # Prepare data for download
            export_data = []
            for category in categories_list:
                for keyword in clusters.get(category, []):
                    export_data.append({"Keyword": keyword, "Basket": category})
            
            for keyword in uncategorized:
                export_data.append({"Keyword": keyword, "Basket": "Other"})
            
            export_df = pd.DataFrame(export_data)
            
            # CSV export
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name="clustered_keywords.csv",
                mime="text/csv"
            )
            
            # TXT export
            txt_data = ""
            for category in categories_list:
                if clusters.get(category):
                    txt_data += f"{category}\n"
                    txt_data += "=" * 50 + "\n"
                    for kw in clusters[category]:
                        txt_data += f"• {kw}\n"
                    txt_data += "\n"
            
            if uncategorized:
                txt_data += "Other\n"
                txt_data += "=" * 50 + "\n"
                for kw in uncategorized:
                    txt_data += f"• {kw}\n"
            
            st.download_button(
                label="📥 Download as TXT",
                data=txt_data,
                file_name="clustered_keywords.txt",
                mime="text/plain"
            )
            
            # JSON export
            json_data = json.dumps(dict(clusters), indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name="clustered_keywords.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")

else:
    st.info("👈 Upload your CSV files in the sidebar to start clustering keywords")
