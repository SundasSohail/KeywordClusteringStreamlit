import streamlit as st
import pandas as pd
import json
import re
from collections import defaultdict
import os

# Page config
st.set_page_config(page_title="Keyword Clustering Tool", layout="wide", initial_sidebar_state="expanded")

# Title and description
st.title("🎯 Keyword Clustering Tool")
st.markdown("Upload your keywords and categories to automatically organize keywords into relevant baskets.")

# Sidebar for file uploads
with st.sidebar:
    st.header("📁 Upload Files")
    
    keywords_file = st.file_uploader("Upload Keywords CSV", type=['csv'])
    categories_file = st.file_uploader("Upload Categories JSON", type=['json'])
    
    st.markdown("---")
    st.subheader("📋 Sample Format")
    st.markdown("**Keywords CSV:**")
    st.code("Keyword\ngerman lederhosen women\ntraditional dirndl\n...")
    
    st.markdown("**Categories JSON:**")
    st.code("""{
  "Category Name": [
    "pattern1.*keyword",
    "pattern2"
  ]
}""")

# Main content
if keywords_file and categories_file:
    try:
        # Load keywords
        df_keywords = pd.read_csv(keywords_file)
        keyword_col = df_keywords.columns[0]
        keywords = df_keywords[keyword_col].tolist()
        
        # Load categories
        categories = json.load(categories_file)
        
        # Clustering function
        def cluster_keywords(keywords, categories):
            """Cluster keywords based on category patterns"""
            clusters = defaultdict(list)
            assigned = set()
            
            # Assign keywords to categories
            for keyword in keywords:
                keyword_lower = keyword.lower()
                assigned_to_category = False
                
                for category_name, patterns in categories.items():
                    for pattern in patterns:
                        try:
                            if re.search(pattern, keyword_lower, re.IGNORECASE):
                                clusters[category_name].append(keyword)
                                assigned.add(keyword)
                                assigned_to_category = True
                                break
                        except re.error:
                            st.warning(f"Invalid regex pattern in {category_name}: {pattern}")
                            continue
                    
                    if assigned_to_category:
                        break
                
                # If not assigned, put in "Other" category
                if keyword not in assigned:
                    clusters['Other'].append(keyword)
            
            return clusters
        
        # Run clustering
        st.info(f"📊 Processing {len(keywords)} keywords with {len(categories)} categories...")
        clusters = cluster_keywords(keywords, categories)
        
        # Display results in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Baskets Overview", "📝 Detailed View", "⬇️ Download Results"])
        
        with tab1:
            # Overview
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Keywords", len(keywords))
                st.metric("Total Baskets", len(clusters))
            
            with col2:
                st.metric("Assigned Keywords", sum(len(kws) for cat, kws in clusters.items() if cat != 'Other'))
                st.metric("Unassigned Keywords", len(clusters.get('Other', [])))
            
            # Basket summary
            st.subheader("Basket Summary")
            summary_data = []
            for cluster_name, kws in sorted(clusters.items()):
                summary_data.append({
                    "Basket Name": cluster_name,
                    "Keywords Count": len(kws)
                })
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        with tab2:
            st.subheader("Detailed Basket View")
            
            for cluster_name in sorted(clusters.keys()):
                keywords_in_basket = clusters[cluster_name]
                
                with st.expander(f"📂 {cluster_name} ({len(keywords_in_basket)} keywords)"):
                    st.markdown("---")
                    for i, keyword in enumerate(keywords_in_basket, 1):
                        st.markdown(f"{i}. **{keyword}**")
        
        with tab3:
            st.subheader("Download Results")
            
            # Format 1: CSV (traditional)
            csv_data = []
            for cluster_id, (cluster_name, kws) in enumerate(sorted(clusters.items())):
                for keyword in kws:
                    csv_data.append({
                        "Basket": cluster_id,
                        "Basket Name": cluster_name,
                        "Keyword": keyword
                    })
            
            df_csv = pd.DataFrame(csv_data)
            csv_download = df_csv.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download as CSV",
                data=csv_download,
                file_name="clustered_keywords.csv",
                mime="text/csv"
            )
            
            # Format 2: Text (readable)
            txt_content = ""
            for cluster_id, (cluster_name, kws) in enumerate(sorted(clusters.items())):
                txt_content += f"Basket {cluster_id}: {cluster_name}\n"
                for keyword in kws:
                    txt_content += f"  - {keyword}\n"
                txt_content += "\n"
            
            txt_download = txt_content.encode('utf-8')
            
            st.download_button(
                label="📄 Download as Text (Readable)",
                data=txt_download,
                file_name="clustered_keywords_readable.txt",
                mime="text/plain"
            )
            
            # Format 3: JSON
            json_data = {}
            for cluster_id, (cluster_name, kws) in enumerate(sorted(clusters.items())):
                json_data[f"Basket {cluster_id}"] = {
                    "name": cluster_name,
                    "keywords": kws
                }
            
            json_download = json.dumps(json_data, indent=2).encode('utf-8')
            
            st.download_button(
                label="📋 Download as JSON",
                data=json_download,
                file_name="clustered_keywords.json",
                mime="application/json"
            )
    
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")

else:
    st.info("👈 Please upload both Keywords CSV and Categories JSON files to get started!")
    
    # Show example section
    with st.expander("💡 Need sample files?"):
        st.markdown("### Sample Categories JSON")
        sample_categories = {
            "Men Clothing": [
                "lederhosen.*men",
                "mens.*lederhosen"
            ],
            "Women Clothing": [
                "dirndl",
                "women.*outfit"
            ],
            "Accessories": [
                "belt",
                "suspender"
            ]
        }
        st.json(sample_categories)
        
        st.markdown("### Sample Keywords CSV")
        sample_keywords = pd.DataFrame({
            "Keyword": [
                "men's lederhosen",
                "women's dirndl",
                "leather belt"
            ]
        })
        st.dataframe(sample_keywords, use_container_width=True, hide_index=True)
