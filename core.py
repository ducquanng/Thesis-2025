# --- Imports and setup ---
import os
import hashlib
import warnings
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from IPython.display import display, Markdown

# Suppress deprecation warnings
warnings.simplefilter("ignore", DeprecationWarning)

# Load environment variables from .env file
load_dotenv()

# --- Config paths and filenames ---
EMBEDDINGS_DIRECTORY = './vstore'
VECTORSTORE_NAME = 'mkb_challenge_store'
EXCEL_FILENAME = "MKB-challenge-data.xlsx"

# Read API credentials from environment
inference = os.getenv("AZURE_AI_ENDPOINT")
apikey = os.getenv("AZURE_AI_KEY")

# --- Utility function to check if extraction output is meaningful ---
def has_relevant_facts(extracted: str) -> bool:
    return extracted.strip() not in ["[]", '""', ""]

# --- Extract relevant facts for a challenge using the LLM ---
def extract_relevant_info(docs, question, chat_model, debug_mode=False):
    relevant_info_list = []
    for doc in docs:
        # Construct system + user prompt for the extractor model
        extraction_messages = [
            SystemMessage(content="You are a challenge information extractor. [...]"),
            HumanMessage(content=f"Question: {question}\n\nArticle:\n{doc.page_content}")
        ]
        # Try to run the model to get extracted facts
        try:
            extracted = chat_model.invoke(extraction_messages).content.strip()
        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            continue

        # Show debug markdown if enabled
        if debug_mode:
            title = doc.metadata.get('title', 'No title')
            debug_msg = (
                f"[Extracted from '{title}']:\n\n{extracted}" if has_relevant_facts(extracted)
                else f"[No useful info from '{title}']"
            )
            display(Markdown(debug_msg))

        # Store extracted info along with metadata
        relevant_info_list.append({
            "title": doc.metadata.get("title", "No title"),
            "url": doc.metadata.get("url", "No URL"),
            "extracted_facts": extracted
        })

    # Filter to only keep useful sources and combine the extracted text
    used_sources = [info for info in relevant_info_list if has_relevant_facts(info["extracted_facts"])]
    combined_text = "\n".join(info["extracted_facts"] for info in used_sources)
    return used_sources, combined_text

# --- Split long texts into chunks for embedding ---
def get_text_chunks(texts_with_metadata):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks, metadatas = [], []
    for text, metadata in texts_with_metadata:
        for chunk in splitter.split_text(text):
            chunks.append(chunk)
            metadatas.append(metadata)
    return chunks, metadatas

# --- Create and store a FAISS vectorstore from text chunks ---
def create_vectorstore(texts, metadatas):
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=inference,
        api_key=apikey,
        azure_deployment="text-embedding-ada-002",
        openai_api_version="2023-05-15"
    )
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    os.makedirs(EMBEDDINGS_DIRECTORY, exist_ok=True)
    vectorstore.save_local(os.path.join(EMBEDDINGS_DIRECTORY, VECTORSTORE_NAME), index_name="index")
    return vectorstore

# --- Load an existing vectorstore from local storage ---
def load_vectorstore():
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=inference,
        api_key=apikey,
        azure_deployment="text-embedding-ada-002",
        openai_api_version="2023-05-15"
    )
    return FAISS.load_local(
        folder_path=os.path.join(EMBEDDINGS_DIRECTORY, VECTORSTORE_NAME),
        index_name="index",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

# --- Initialize a chat model for generating text ---
def initialize_chat_models():
    return {
        "chat": AzureChatOpenAI(
            azure_endpoint=inference,
            api_key=apikey,
            azure_deployment="gpt-4",
            openai_api_version="2023-05-15"
        )
    }

# --- Generate a personalized cold-email using RAG & GPT ---
def generate_cold_email(challenge_name: str, company_name: str, vectorstore, chat_model) -> str:
    # Step 1: Search for similar documents based on challenge name
    docs = vectorstore.similarity_search(challenge_name, k=6)

    # Step 2: Filter documents to exact title match
    filtered_docs = [doc for doc in docs if doc.metadata.get("title", "").strip().lower() == challenge_name.strip().lower()]
    if not filtered_docs:
        return f"Geen exacte match gevonden voor '{challenge_name}'."

    # Step 3: Extract challenge-specific facts
    used_sources, combined_text = extract_relevant_info(filtered_docs, challenge_name, chat_model)
    if not combined_text.strip():
        return "Geen relevante informatie gevonden voor deze uitdaging."

    # Step 4: Prompt the model to generate email using AIDA framework
    email_prompt = [
        SystemMessage(content="""[...]"""),  # 👈 detailed system prompt for generating persuasive emails
        HumanMessage(content=f"Challenge info:\n{combined_text}\n\nCompany name: {company_name}")
    ]
    email = chat_model.invoke(email_prompt).content.strip()
    return email

# --- Create a hash of an Excel file for change tracking ---
def get_excel_hash(filename: str) -> str:
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# --- Load vectorstore if it exists and is up to date; otherwise, recreate it ---
def load_or_create_vectorstore(excel_path: str):
    hash_path = os.path.join(EMBEDDINGS_DIRECTORY, VECTORSTORE_NAME, "hash.txt")
    vectorstore_path = os.path.join(EMBEDDINGS_DIRECTORY, VECTORSTORE_NAME, "index.faiss")
    current_hash = get_excel_hash(excel_path)
    stored_hash = None

    # Check if hash file exists and read stored hash
    if os.path.exists(hash_path):
        with open(hash_path, 'r') as f:
            stored_hash = f.read().strip()

    # Recreate vectorstore if missing or outdated
    if not os.path.exists(vectorstore_path) or stored_hash != current_hash:
        df = pd.read_excel(excel_path).fillna("")
        texts_with_metadata = [
            (" | ".join(f"{col}: {row[col]}" for col in df.columns), {
                "title": row.get("Challenge Name", "No title"),
                "url": row.get("URL", "No URL"),
                "source": "MKB-challenge-data"
            })
            for _, row in df.iterrows()
        ]
        chunks, metadatas = get_text_chunks(texts_with_metadata)
        vectorstore = create_vectorstore(chunks, metadatas)

        # Save current hash
        os.makedirs(os.path.dirname(hash_path), exist_ok=True)
        with open(hash_path, 'w') as f:
            f.write(current_hash)
    else:
        vectorstore = load_vectorstore()
    return vectorstore

# --- Split user input (Challenge Name | Company Name) ---
def parse_input(user_input: str) -> tuple:
    parts = user_input.split('|')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None
