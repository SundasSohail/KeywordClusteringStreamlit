import argparse
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import re


def cluster_keywords(input_file, output_file, separator, keyword_col, mode='semantic', similarity_threshold=0.6):
    """
    Cluster keywords using semantic categories or similarity-based clustering
    
    Modes:
    - 'semantic': Groups keywords by semantic meaning (clothing categories)
    - 'similarity': Groups keywords by Jaccard similarity with other keywords
    """
    
    # Load data
    data = pd.read_csv(input_file, sep=separator, engine='python')
    
    # Extract keywords
    if isinstance(data[keyword_col].iloc[0], str):
        keywords = data[keyword_col].tolist()
    else:
        keywords = [str(k) for k in data[keyword_col].tolist()]
    
    if mode == 'semantic':
        clusters, category_names = semantic_cluster_keywords(keywords)
    else:
        clusters, category_names = similarity_cluster_keywords(keywords, float(similarity_threshold))
    
    # Save in two formats: CSV and readable format
    # Format 1: CSV with basket info
    clustered_keywords = [(cluster_id, category_names.get(cluster_id, f'Cluster {cluster_id}'), keyword)
                          for cluster_id, cluster in enumerate(clusters)
                          for keyword in cluster]
    
    clustered_keywords_df = pd.DataFrame(clustered_keywords, columns=['Basket', 'Basket Name', 'Keyword'])
    clustered_keywords_df.to_csv(output_file, index=False)
    
    # Format 2: Readable format with basket headers
    readable_file = output_file.replace('.csv', '_readable.csv')
    with open(readable_file, 'w', encoding='utf-8') as f:
        for cluster_id, cluster in enumerate(clusters):
            basket_name = category_names.get(cluster_id, f'Cluster {cluster_id}')
            f.write(f"Basket {cluster_id}: {basket_name}\n")
            for keyword in cluster:
                f.write(f"  - {keyword}\n")
            f.write("\n")


def semantic_cluster_keywords(keywords):
    """
    Cluster keywords based on semantic categories and patterns
    Organizes keywords into relevant baskets for e-commerce
    Returns: (clusters, category_names)
    """
    
    # Define semantic categories and their keywords/patterns
    # Categories are processed in order - first match wins
    categories = {
        'Men Lederhosen & Outfits': [
            'lederhosen.*men(?!.*shirt|.*shoe|.*sock)',
            'mens.*lederhosen(?!.*shirt|.*shoe|.*sock)',
            'male.*lederhosen(?!.*shirt|.*shoe|.*sock)',
            'lederhosen.*male(?!.*shirt|.*shoe|.*sock)',
            'traditional.*lederhosen(?!.*women|.*female|.*shirt|.*shoe)',
            'german.*lederhosen(?!.*women|.*female|.*shirt|.*shoe)',
            'german.*lederhosen.*outfit',
            'german.*lederhosen.*male',
            'lederhosen.*outfit',
            'oktoberfest.*herren',
            'outfit.*herren',
            'traditional.*german.*lederhosen',
            'long.*lederhosen.*pants',
            'plus.*size.*lederhosen',
        ],
        'Women Outfits & Clothing': [
            'women.*outfit',
            'female.*outfit',
            'womens.*outfit',
            'womens.*clothing',
            'women.*clothing',
            'traditional.*german.*female',
            'german.*female.*outfit',
            'german.*female',
            'traditional.*german.*outfit(?!.*men|.*male)',
            'oktoberfest.*women',
            'oktoberfest.*clothing.*women',
            'oktoberfest.*dresses',
        ],
        'Oktoberfest General': [
            'oktoberfest.*costume',
            'oktoberfest(?!.*dirndl|.*women|.*men|.*shoe|.*shirt|.*sock)',
            'german.*outfit(?!.*female|.*women)',
        ],
        'Women Dirndl & Dresses': [
            'dirndl',
            'women.*dirndl',
            'german.*dirndl',
            'oktoberfest.*dirndl',
            'dirndl.*size',
        ],
        'Accessories': [
            'suspender',
            'belt',
            'bundhosen',
            'bavarian.*trachten',
        ],
        'Men Shoes & Socks': [
            'lederhosen.*shoe',
            'shoes.*lederhosen',
            'mens.*shoe',
            'oktoberfest.*shoe',
            'mens.*oktoberfest.*shoe',
            'lederhosen.*sock',
            'socks.*lederhosen',
            'oktoberfest.*sock',
            'mens.*oktoberfest.*sock',
        ],
        'Men Shirts': [
            'lederhosen.*shirt',
            'shirt.*lederhosen',
            'mens.*shirt',
            'mens.*oktoberfest.*shirt',
            'oktoberfest.*shirt',
            'lederhosen.*shirts',
            'shirt.*men',
        ],
    }
    
    clusters = defaultdict(list)
    category_names = {}
    assigned = set()
    cluster_id = 0
    
    # Assign keywords to categories in order
    for category_name, patterns in categories.items():
        for keyword in keywords:
            if keyword in assigned:
                continue
            keyword_lower = keyword.lower()
            for pattern in patterns:
                if re.search(pattern, keyword_lower, re.IGNORECASE):
                    clusters[cluster_id].append(keyword)
                    category_names[cluster_id] = category_name
                    assigned.add(keyword)
                    break
        
        if clusters[cluster_id]:
            cluster_id += 1
    
    # Add unassigned keywords to "Other" category
    other_keywords = [kw for kw in keywords if kw not in assigned]
    if other_keywords:
        clusters[cluster_id] = other_keywords
        category_names[cluster_id] = 'Other'
    
    return [clusters[i] for i in sorted(clusters.keys())], category_names


def similarity_cluster_keywords(keywords, similarity_threshold):
    """
    Cluster keywords based on Jaccard similarity of keyword tokens
    Returns: (clusters, category_names)
    """
    
    def jaccard_similarity(tokens1, tokens2):
        intersection = len(list(set(tokens1).intersection(tokens2)))
        union = (len(set(tokens1)) + len(set(tokens2))) - intersection
        return float(intersection) / union if union > 0 else 0
    
    # Tokenize keywords (split by spaces and common delimiters)
    keyword_tokens = {}
    for keyword in keywords:
        tokens = re.split(r'[-\s_]+', keyword.lower().strip())
        tokens = [t for t in tokens if t]  # Remove empty tokens
        keyword_tokens[keyword] = set(tokens)
    
    # Find clusters based on token similarity
    clusters = []
    for keyword, tokens in tqdm(keyword_tokens.items(), desc='Creating clusters'):
        # Find a cluster that this keyword belongs to
        found_cluster = False
        for cluster in clusters:
            if any(jaccard_similarity(tokens, keyword_tokens[other_keyword]) >= similarity_threshold
                   for other_keyword in cluster):
                cluster.append(keyword)
                found_cluster = True
                break
        
        if not found_cluster:  # no suitable cluster found
            clusters.append([keyword])
    
    # Generate category names for similarity clusters
    category_names = {i: f'Cluster {i}' for i in range(len(clusters))}
    
    return clusters, category_names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cluster keywords by semantic meaning or similarity",
        epilog="Examples:\n"
               "  Semantic clustering: python jaccard-score-cli.py -m semantic sample_keywords.csv output.csv\n"
               "  Similarity clustering: python jaccard-score-cli.py -m similarity -t 0.5 sample_keywords.csv output.csv"
    )
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to save the output clustered keywords")
    parser.add_argument("-s", "--separator", default=',', help="Separator of the input file (default: ',')")
    parser.add_argument("-k", "--keyword_col", default='Keyword', help="Name of the keyword column (default: 'Keyword')")
    parser.add_argument("-m", "--mode", default='semantic', choices=['semantic', 'similarity'],
                       help="Clustering mode: 'semantic' for category-based clustering, 'similarity' for token-based clustering (default: 'semantic')")
    parser.add_argument("-t", "--similarity_threshold", default=0.6, help="Threshold of similarity for similarity mode (default: 0.6)")

    args = parser.parse_args()
    
    cluster_keywords(args.input_file, args.output_file, args.separator, args.keyword_col, args.mode, args.similarity_threshold)
    print("")
    print("✓ Keywords clustered successfully!")
    print(f"Output saved to: {args.output_file}")
    print(f"Readable format saved to: {args.output_file.replace('.csv', '_readable.csv')}")