import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import csv
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

# Useful if you want to perform stemming.
import nltk
stemmer = nltk.stem.PorterStemmer()

categories_file_name = r'/workspace/datasets/product_data/categories/categories_0001_abcat0010000_to_pcmcat99300050000.xml'

queries_file_name = r'/workspace/datasets/train.csv'
output_file_name = r'/workspace/search_with_machine_learning_course/datasets/fasttext/labeled_query_data.txt'

parser = argparse.ArgumentParser(description='Process arguments.')
general = parser.add_argument_group("general")
general.add_argument("--min_queries", default=1,  help="The minimum number of queries per category label (default is 1)")
general.add_argument("--output", default=output_file_name, help="the file to output to")

args = parser.parse_args()
output_file_name = args.output

if args.min_queries:
    min_queries = int(args.min_queries)

# The root category, named Best Buy with id cat00000, doesn't have a parent.
root_category_id = 'cat00000'
tree = ET.parse(categories_file_name)
root = tree.getroot()

# Parse the category XML file to map each category id to its parent category id in a dataframe.
categories = []
parents = []
for child in root:
    cat_path = child.find('path')
    cat_path_ids = [cat.find('id').text for cat in cat_path]
    leaf_id = cat_path_ids[-1]
    if leaf_id != root_category_id:
        categories.append(leaf_id)
        parents.append(cat_path_ids[-2])
parents_df = pd.DataFrame(list(zip(categories, parents)), columns =['category', 'parent'])

# Read the training data into pandas, only keeping queries with non-root categories in our category tree.
df = pd.read_csv(queries_file_name)[['category', 'query']]
df = df[df['category'].isin(categories)]

def get_parents(children):
    parents = []
    for child in children:
        parents.append(parents_df[parents_df['category'] == child]['parent'].values[0] if parents_df[parents_df['category'] == child]['parent'].size > 0 else root_category_id)
    return parents

def canonicalize(query):
    query = query.lower()
    query = query.translate ({ord(c): " " for c in "\ââ®™!@#$%^&*()[]\{\};:,./<>?\|`~-=_+"})
    query = query.replace(u"\u2122", '').replace(u"\u00AE", '')

    snowball = SnowballStemmer("english")
    tokens = nltk.word_tokenize(query)
    tokens = [token for token in tokens if (token not in stopwords.words('english') and token.isalnum())]
    tokens = [snowball.stem(token) for token in tokens]
    query = ' '.join(tokens)

    return query

df['canonicalized_query'] = df.apply(lambda row: canonicalize(row.query), axis=1)

min_category_count = df.groupby("category").count().min().query
while min_category_count < min_queries:
    underrepresented = list(dict.fromkeys(df.groupby("category").filter(lambda x: len(x) < min_queries)['category'].tolist()))
    underrepresented_parents = get_parents(underrepresented)
    df['category'] = df['category'].replace(underrepresented, underrepresented_parents)
    min_category_count = df.groupby("category").count().min().query

print("After rolling up to ancestors to meet min_queries requirement, our model is left with {} distinct categories.".format(df.category.nunique()))

# Create labels in fastText format.
df['label'] = '__label__' + df['category']

# Output labeled query data as a space-separated file, making sure that every category is in the taxonomy.
df = df[df['category'].isin(categories)]
df['output'] = df['label'] + ' ' + df['canonicalized_query']
df[['output']].to_csv(output_file_name, header=False, sep='|', escapechar='\\', quoting=csv.QUOTE_NONE, index=False)