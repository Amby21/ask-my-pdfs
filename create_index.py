from azure.identity import DefaultAzureCredential
import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
)
SEARCH_ENDPOINT = os.environ["SEARCH_ENDPOINT"]
client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=DefaultAzureCredential())

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="page",type=SearchFieldDataType.Int32,filterable=True),
    SearchableField(name="text", type=SearchFieldDataType.String),
    SearchField(name="vector",type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,vector_search_dimensions=1536, vector_search_profile_name="vprofile")

]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
    profiles=[VectorSearchProfile(name="vprofile", algorithm_configuration_name="hnsw")],
)

index = SearchIndex(name="ipod-guide-index", fields=fields, vector_search=vector_search)
client.create_or_update_index(index)          # safe to run twice: it updates instead of failing

# confirm: read it back and print each field's name
for f in client.get_index("ipod-guide-index").fields:
    print(f.name, f.type)