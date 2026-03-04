from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions

# Path to your single file and ChromaDB
FILE_PATH = r"source.txt"
CHROMA_PATH = r"chroma_db"

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Embedding model
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="webpages", embedding_function=embedding_fn
)

# Load single text file
loader = TextLoader(FILE_PATH, encoding="utf-8")
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
    separators=["\n\n", "\n", " "],
    length_function=len
)

chunks = text_splitter.split_documents(documents)

# Prepare for ChromaDB insertion
docs, metadata, ids = [], [], []
for i, chunk in enumerate(chunks):
    docs.append(chunk.page_content)
    ids.append(f"ID{i}")
    metadata.append(chunk.metadata)

# Insert into ChromaDB
collection.upsert(
    documents=docs,
    metadatas=metadata,
    ids=ids
)

print(f"✅ Successfully embedded {len(docs)} chunks into ChromaDB from {FILE_PATH}.")
