import os
import requests

from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, FuzzyTermPlugin, OrGroup
from whoosh.query import FuzzyTerm, Term

import os

# Get the current working directory
current_dir = os.getcwd()

def create_search_index(directory):
    schema = Schema(title=ID(stored=True), content=TEXT)
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                writer.add_document(title=filename, content=content)
    
    writer.commit()

def search_in_index(search_pattern):
    result_files = []
    ix = open_dir("../../data/rag/indexdir")
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(search_pattern)
        results = searcher.search(query)
        for result in results:
            result_files.append(result['title'])

    return result_files


def search_in_index_2(search_pattern):
    result_files = []
    
    ix = open_dir(f"../data/rag/indexdir")
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)
        parser.add_plugin(FuzzyTermPlugin())
        query = parser.parse(f"{search_pattern}~3")  
        results = searcher.search(query)
        for result in results:
            result_files.append(result['title'])
    return result_files


def search_in_index_3(search_pattern):
    ix = open_dir(f"../data/rag/indexdir")
    result_files = []
    
    max_distance = 4

    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema, group=OrGroup.factory(0.9))  # Adjusting the OR group boost factor
        parser.add_plugin(FuzzyTermPlugin())
        
        # Increase the fuzziness and use wildcard for broader matching
        fuzzy_query = FuzzyTerm("content", search_pattern, maxdist=max_distance)
        wildcard_query = Term("content", f"{search_pattern}*")
        
        # Combine queries
        query = parser.parse(f"{search_pattern}~{max_distance} OR {search_pattern}*")
        
        # Execute search and collect results
        results = searcher.search(query)
        for result in results:
            result_files.append(result['title'])
    
    return result_files