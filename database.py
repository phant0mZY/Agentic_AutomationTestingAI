from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions


FILE_PATH = r"source.txt"
CHROMA_PATH = r"chroma_db"


chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)


embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


collection = chroma_client.get_or_create_collection(
    name="webpages", embedding_function=embedding_fn
)


loader = TextLoader(FILE_PATH, encoding="utf-8")
documents = loader.load()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
    separators=["\n\n", "\n", " "],
    length_function=len
)

chunks = text_splitter.split_documents(documents)


docs, metadata, ids = [], [], []
for i, chunk in enumerate(chunks):
    docs.append(chunk.page_content)
    ids.append(f"ID{i}")
    metadata.append(chunk.metadata)


collection.upsert(
    documents=docs,
    metadatas=metadata,
    ids=ids
)

print(f"✅ Successfully embedded {len(docs)} chunks into ChromaDB from {FILE_PATH}.")

