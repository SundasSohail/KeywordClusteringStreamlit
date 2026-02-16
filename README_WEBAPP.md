# Keyword Clustering Tool - User Interface Version

An interactive web-based tool to automatically cluster and organize keywords into relevant baskets based on custom category definitions.

## Features ✨

- 🎯 **Interactive Web UI** - Clean, intuitive Streamlit interface
- 📁 **Custom Categories** - Define your own categories with regex patterns
- 📊 **Multiple Export Formats** - CSV, TXT, and JSON outputs
- 📈 **Real-time Analytics** - View clustering statistics instantly
- 🔍 **Detailed Basket View** - Explore keywords in each basket
- ⚙️ **No Configuration** - Just upload files and go!

## Installation

### Requirements
- Python 3.8+
- pandas
- streamlit

### Setup

1. Install dependencies:
```bash
pip install streamlit pandas
```

2. Make sure you have the files:
   - `app.py` - The Streamlit web application
   - `categories.json` - Category definitions (optional, can upload your own)
   - `sample_keywords.csv` - Sample keywords file

## Usage

### Quick Start

1. **Start the app:**
```bash
python -m streamlit run app.py
```

2. **Open in browser:**
The app will automatically open at `http://localhost:8501`

### How to Use

#### Step 1: Prepare Your Files

**Keywords CSV File:**
```csv
Keyword
german lederhosen women
traditional dirndl dress
men's shirt
leather belt
```

**Categories JSON File:**
```json
{
  "Men Clothing": [
    "lederhosen.*men",
    "mens.*outfit"
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
```

#### Step 2: Upload Files
- Click "Upload Keywords CSV" and select your keywords file
- Click "Upload Categories JSON" and select your categories file

#### Step 3: View Results
- **Baskets Overview** - See summary of all baskets and their counts
- **Detailed View** - Expand baskets to see individual keywords
- **Download Results** - Export in CSV, TXT, or JSON format

## File Formats

### Keywords CSV
- First row: Header (e.g., "Keyword")
- Subsequent rows: Keywords to cluster
- Delimiter: Comma (,) by default

### Categories JSON
Structure:
```json
{
  "Category Name": [
    "regex_pattern_1",
    "regex_pattern_2",
    "regex_pattern_3"
  ],
  "Another Category": [
    "another_pattern"
  ]
}
```

**Pattern Tips:**
- Use `.*` for "any characters"
- Use `(?!...)` for negative lookahead (exclude patterns)
- Use `|` for alternation (multiple options)
- Patterns are case-insensitive by default

**Examples:**
```json
{
  "Men Lederhosen": [
    "lederhosen.*men",
    "lederhosen.*male",
    "mens.*lederhosen(?!.*shirt)"
  ],
  "Women Clothing": [
    "dirndl",
    "women.*outfit",
    "female.*clothing"
  ],
  "Shirts": [
    "shirt(?!.*dress)",
    "t-shirt",
    "tshirt"
  ]
}
```

## Output Formats

### 1. CSV Format (for databases/spreadsheets)
```csv
Basket,Basket Name,Keyword
0,Men Clothing,men's lederhosen
0,Men Clothing,mens shirt
1,Women Clothing,dirndl dress
```

### 2. TXT Format (human-readable)
```
Basket 0: Men Clothing
  - men's lederhosen
  - mens shirt

Basket 1: Women Clothing
  - dirndl dress
  - woman's outfit
```

### 3. JSON Format
```json
{
  "Basket 0": {
    "name": "Men Clothing",
    "keywords": ["men's lederhosen", "mens shirt"]
  },
  "Basket 1": {
    "name": "Women Clothing",
    "keywords": ["dirndl dress"]
  }
}
```

## Command Line Tools (Legacy)

The original command-line tool is still available:

```bash
# Semantic clustering (default)
python jaccard-score-cli.py sample_keywords.csv output.csv

# With custom separator
python jaccard-score-cli.py -s ',' sample_keywords.csv output.csv

# Help
python jaccard-score-cli.py --help
```

## Sample Categories File

A sample `categories.json` is included with default Oktoberfest/Lederhosen categories:
- Men Lederhosen & Outfits
- Women Outfits & Clothing
- Women Dirndl & Dresses
- Men Shirts
- Men Shoes & Socks
- Accessories
- Oktoberfest General

## Troubleshooting

### Invalid regex pattern error
- Check your JSON syntax in the categories file
- Test your regex patterns online (regex101.com)
- Ensure proper escaping of special characters

### Keywords not being clustered
- Check that your patterns match the keywords
- Patterns are case-insensitive but spaces matter
- Remember to use `.*` to skip characters: `shirt` matches "shirt" only, but `shirt.*` matches "shirt abc"

### File upload issues
- Ensure CSV has proper comma delimiters
- Ensure JSON is valid (no trailing commas)
- Check file encoding is UTF-8

## Advanced Pattern Examples

```json
{
  "Men & Women Mixed": [
    "outfit(?!.*sale)"
  ],
  "Exclude Sales": [
    "(?!.*sale).*lederhosen"
  ],
  "Multi-word": [
    "german.*outfit",
    "traditional.*dirndl"
  ],
  "Alternatives": [
    "shirt|tshirt|t-shirt"
  ]
}
```

## Performance

- Handles up to 10,000+ keywords easily
- Real-time clustering feedback
- Instant category matching using regex

## Tips for Best Results

1. **Keep patterns simple** - Complex regex can slow things down
2. **Order categories strategically** - First matching pattern wins
3. **Be specific** - Use `(?!...)` to exclude unwanted matches
4. **Test patterns** - Use regex101.com to verify patterns
5. **Use wildcards wisely** - `.*` can be greedy

## License

MIT License

## Support

For issues or suggestions, check the source code or contact the developer.

---

**Happy Clustering! 🎯**
