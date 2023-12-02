"""
This module scans a directory for Markdown (.md) files and generates an index of words
found in those files. It filters out common stop words and uses natural language processing
to lemmatize words and filter by part-of-speech. The index is then saved to a Markdown file.
"""

import os
import re
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# Download necessary NLTK datasets
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Set of English stop words
stop_words = set(stopwords.words('english'))
# Add custom stop words
custom_stop_words = {'also', 'ask', 'asked'}
stop_words.update(custom_stop_words)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()


def is_valid_word(pos):
    """
    Determines if a part-of-speech tag is valid for inclusion in the index.

    Args:
        pos (str): The part-of-speech tag of the word.

    Returns:
        bool: True if the part-of-speech tag is allowed, False otherwise.
    """
    allowed_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'JJ'}  # Nouns and adjectives
    return pos in allowed_pos


def extract_words_from_file(md_file_path):
    """
    Extracts and processes words from a Markdown file.

    This function reads a file, removes code blocks, tokenizes the text,
    lemmatizes the words, and filters out stop words, numbers, single-character
    words, and words based on part-of-speech.

    Args:
        md_file_path (str): The path to the Markdown file.

    Returns:
        list: A list of processed words from the file.
    """
    try:
        with open(md_file_path, 'r', encoding='utf-8') as md_file:
            markdown_text = md_file.read()
            markdown_text = re.sub(r'`[^`]+`', '', markdown_text)
            words_in_file = re.findall(r'\b\w+\b', markdown_text.lower())
            tagged_words = pos_tag(words_in_file)
            processed_words = [lemmatizer.lemmatize(w) for w, pos in tagged_words
                               if w not in stop_words and len(w) > 1
                               and not w.isdigit() and is_valid_word(pos)]
            return processed_words
    except IOError as e:
        print(f"Error reading file: {md_file_path}")
        print(f"I/O error: {e}")
        return []


def scan_directory(directory):
    """
    Scans a directory recursively for Markdown files and extracts words from them.

    Args:
        directory (str): The path to the directory to scan.

    Returns:
        dict: A dictionary where keys are file paths and
              values are lists of words found in each file.
    """
    markdown_files = {}
    for root, _, md_files in os.walk(directory):  # Replace 'dirs' with '_'
        for md_file in md_files:
            if md_file.endswith('.md'):
                full_path = os.path.join(root, md_file)
                markdown_files[full_path] = extract_words_from_file(full_path)
    return markdown_files


word_occurrences = defaultdict(list)

markdown_directory = os.path.abspath("typora-notes/")
indexed_markdown_files = scan_directory(markdown_directory)

for path, extracted_words in indexed_markdown_files.items():
    for extracted_word in extracted_words:
        word_occurrences[extracted_word].append(path)

sorted_words = sorted(word_occurrences.keys())

index_file_path = os.path.join(markdown_directory, "index.md")
with open(index_file_path, "w", encoding='utf-8') as index_md_file:
    index_md_file.write("# Encyclopedia Index\n\n")
    for sorted_word in sorted_words:
        index_md_file.write(f"## {sorted_word}\n\n")
        occurrences = word_occurrences[sorted_word]
        for occurrence in occurrences:
            relative_file_path = os.path.relpath(occurrence, markdown_directory)
            relative_file_path = relative_file_path.replace('\\', '/')
            index_md_file.write(f"- [{relative_file_path}]({relative_file_path})\n")

print("Index generation completed.")
