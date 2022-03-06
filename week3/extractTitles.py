import os
import random
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.tokenize import RegexpTokenizer
import string

directory = r'/workspace/search_with_machine_learning_course/data/pruned_products'
parser = argparse.ArgumentParser(description='Process some integers.')
general = parser.add_argument_group("general")
general.add_argument("--input", default=directory,  help="The directory containing the products")
general.add_argument("--output", default="/workspace/datasets/fasttext/titles.txt", help="the file to output to")

# Consuming all of the product data takes a while. But we still want to be able to obtain a representative sample.
general.add_argument("--sample_rate", default=0.1, type=float, help="The rate at which to sample input (default is 0.1)")

args = parser.parse_args()
output_file = args.output
path = Path(output_file)
output_dir = path.parent
if os.path.isdir(output_dir) == False:
        os.mkdir(output_dir)

if args.input:
    directory = args.input

sample_rate = args.sample_rate

def transform_training_data(name):
    # name = name.replace('\n', ' ').lower()
    # name = name.replace(u"\u2122", '').replace(u"\u00AE", '')

    # name = name.translate(str.maketrans('', '', string.punctuation))

    # # snowball = SnowballStemmer("english")
    # # tokenizer = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)
    # tokens = word_tokenize(name)
    # # tokens = tokenizer.tokenize(name)
    # tokens = [token for token in tokens if token not in stopwords.words('english')]
    # # tokens = [snowball.stem(token) for token in tokens]
    # name = ' '.join(tokens)
    # # name = name.encode('ascii', "ignore").decode('ascii')

    # tokenizer = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)
    # snowball = SnowballStemmer("english")

    # name = name.replace('\n', ' ').lower()
    # tokens = tokenizer.tokenize(name)
    # tokens = [snowball.stem(token) for token in tokens]
    # name = " ".join(tokens)
    # return name
    stemmer = SnowballStemmer("english")
    cleaned = ''.join([i for i in name.lower() if i not in string.punctuation])
    tokens = nltk.word_tokenize(cleaned)
    tokens = [token for token in tokens if token not in stopwords.words('english')]
    return " ".join([stemmer.stem(token.replace(u"\u2122", '').replace(u"\u00AE", '')) for token in tokens])
    # return name

# Directory for product data

print("Writing results to %s" % output_file)
with open(output_file, 'w') as output:
    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            f = os.path.join(directory, filename)
            tree = ET.parse(f)
            root = tree.getroot()
            for child in root:
                if random.random() > sample_rate:
                    continue
                if (child.find('name') is not None and child.find('name').text is not None):
                    name = transform_training_data(child.find('name').text)
                    output.write(name + "\n")
