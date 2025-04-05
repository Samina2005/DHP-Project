from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

df = pd.read_csv("dhp_project/sitare.csv")
df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
df['Year'] = df['Time'].dt.year
df_clean = df.dropna(subset=['Tag', 'Year'])
total_per_year = df_clean.groupby('Year').size().rename('total_count')
tag_counts = df_clean.groupby(['Year', 'Tag']).size().reset_index(name='count')
tag_counts = tag_counts.merge(total_per_year, on='Year')
tag_counts['normalized_count'] = (tag_counts['count'] / tag_counts['total_count']) * 100  
top_tags_by_year = (
        tag_counts.sort_values(['Year', 'normalized_count'], ascending=[True, False])
        .groupby('Year')
        .head(10)
    )
result = {}
for year, group in top_tags_by_year.groupby('Year'):
    result[str(year)] = group[['Tag', 'normalized_count']].rename(columns={'Tag': 'tag', 'normalized_count': 'count'}).to_dict(orient='records')
    
@app.route('/api/top-tags-by-year')
def get_top_tags():
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
