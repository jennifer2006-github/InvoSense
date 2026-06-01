import os
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini (using the new google-genai SDK)
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None

# Setup ChromaDB (Local Vector Store)
# We store the db in a 'chroma_db' folder inside backend
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="policy_docs")

# Setup Embedding Model
# This downloads a small, fast local model for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Setup Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

def add_document(text: str, filename: str):
    """Chunks text and adds to ChromaDB."""
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        return 0

    # Generate embeddings
    embeddings = embedding_model.encode(chunks).tolist()
    
    # Generate IDs
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    
    # Add metadata
    metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]
    
    # Add to collection
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    
    return len(chunks)


def ask_question(query: str) -> str:
    """Retrieves context and asks the LLM."""
    if not gemini_client:
        return "⚠️ GEMINI_API_KEY is missing or invalid in your .env file. Please add it to use the chatbot."

    # 1. Embed the query
    query_embedding = embedding_model.encode([query]).tolist()[0]
    
    # 2. Retrieve top 3 relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "I don't have any uploaded documents to answer that yet. Please upload a policy document first."
    
    # 3. Construct context
    retrieved_chunks = results['documents'][0]
    context = "\n\n---\n\n".join(retrieved_chunks)
    
    # 4. Prompt the LLM
    prompt = f"""You are a helpful AI assistant for the InvoSense application. 
Use the following context from uploaded policy documents to answer the user's question. 
If the answer is not in the context, say "I couldn't find the answer in the uploaded documents."

Context:
{context}

Question: {query}
Answer:"""

    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text
