import os
import re
import numpy as np
from langchain_openai.chat_models import ChatOpenAI     
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from googleapiclient.discovery import build
import pinecone 
from pinecone.core.client.exceptions import NotFoundException
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs


# Load environment variables from .env file
load_dotenv()

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Pinecone client globally
pc = pinecone.Pinecone(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_API_ENV
)

# Initialize OpenAI model
#model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o")
model = ChatGroq(temperature=0, model="llama3-70b-8192")
parser = StrOutputParser()


# Define prompt template
template = """
#answer the question based on the youtube video transcript context provided below
#if the answer cannot be generated from the transcript, reply "Your question was not found in the video transcript".
#Answer in markdown format


#Context: {context}

#Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def is_valid_youtube_url(url):
    # Patterns for YouTube URLs
    youtube_patterns = [
        r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$',
        r'^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=[\w-]{11}$',
        r'^(https?:\/\/)?(www\.)?youtu\.be\/[\w-]{11}$'
    ]
    
    # Check if the URL matches any of the patterns
    if not any(re.match(pattern, url) for pattern in youtube_patterns):
        return False
    
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check for youtu.be domain
    if parsed_url.netloc == 'youtu.be':
        return len(parsed_url.path) == 12  # /xxxxxxxxxxx (11 characters)
    
    # Check for youtube.com domain
    if parsed_url.netloc in ['youtube.com', 'www.youtube.com']:
        query = parse_qs(parsed_url.query)
        return 'v' in query and len(query['v'][0]) == 11
    
    return False


def get_video_id(youtube_url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_url)
    if video_id_match:
        return video_id_match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = " ".join([entry['text'].replace('\n', ' ') for entry in transcript_list])
    return transcript

def load_transcript_from_youtube(youtube_url):
    try:
        video_id = get_video_id(youtube_url)
        transcript = get_transcript(video_id)
        return transcript
    except Exception as e:
        return f"An error occurred: {e}"
    
def get_video_title(video_id):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    title = response['items'][0]['snippet']['title']
    return title

def initialize_pinecone(transcript, namespace):
    print("initializing pinecone")
    index_name = "youtube-index"
    print("docs splitted ")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    documents = text_splitter.split_text(transcript)

    print("initializing embeddings")
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    print("creating pincone store")
    # Create Pinecone vector store with namespace
    pinecone_store = PineconeVectorStore.from_texts(
       documents, embeddings, index_name=index_name, namespace=namespace
    )
    print(f"Namespace '{namespace}' created in index '{index_name}'.")

    return pinecone_store

def truncate_chat_history(chat_history, max_tokens=2000):
    total_tokens = 0
    truncated_history = []

    for entry in reversed(chat_history):
        question_tokens = len(entry['question'].split())
        response_tokens = len(entry['response'].split())
        entry_tokens = question_tokens + response_tokens
        
        if total_tokens + entry_tokens <= max_tokens:
            truncated_history.append(entry)
            total_tokens += entry_tokens
        else:
            break
    
    truncated_history.reverse()
    return truncated_history
""""
def clear_pinecone_namespace(namespace, index_name):
    try:
        # Initialize Pinecone client
        pc = pinecone.Pinecone(
            api_key=os.environ["PINECONE_API_KEY"],
            environment=os.environ["PINECONE_API_ENV"]
        )

        # Check if the index exists
        if index_name not in pc.list_indexes().names():
            print(f"Index '{index_name}' does not exist.")
            return

        # Connect to the index
        index = pc.Index(index_name)
        
        # Delete all vectors in the specified namespace
        index.delete(delete_all=True, namespace=namespace)
        print(f"Namespace '{namespace}' cleared in index '{index_name}'.")
    except NotFoundException:
        print(f"Namespace '{namespace}' not found in index '{index_name}'.")
"""
def clear_pinecone_namespace(namespace, index_name, force_clear):
    try:
        # Initialize Pinecone client
        pc = pinecone.Pinecone(
            api_key=os.environ["PINECONE_API_KEY"],
            environment=os.environ["PINECONE_API_ENV"]
        )

        # Check if the index exists
        if index_name not in pc.list_indexes().names():
            print(f"Index '{index_name}' does not exist.")
            return

        # Connect to the index
        index = pc.Index(index_name)
        
        # Get the number of vectors in the namespace
        stats = index.describe_index_stats()
        namespace_vector_count = stats.namespaces.get(namespace, {}).get('vector_count', 0)
        
        # Check if the number of vectors exceeds 10
        if namespace_vector_count > 300 or force_clear:
            # Delete all vectors in the specified namespace
            index.delete(delete_all=True, namespace=namespace)
            print(f"Namespace '{namespace}' cleared in index '{index_name}'. {namespace_vector_count} vectors were deleted.")
        else:
            print(f"Namespace '{namespace}' has {namespace_vector_count} vectors, which is not more than 20. No vectors were deleted.")
            return
    
    except NotFoundException:
        print(f"Namespace '{namespace}' not found in index '{index_name}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_pinecone_store(user_id):
  
    # Get the index
    index_name = "youtube-index"
    index = pc.Index(index_name)
    
    # Check if the namespace (user_id) exists in the index
    stats = index.describe_index_stats()
    str_user_id = str(user_id)  # Convert user_id to string
    
    print(f"Checking for user_id: {str_user_id}")
    print(f"Available namespaces: {stats['namespaces']}")
    
    if str_user_id not in stats['namespaces']:
        print(f"Namespace not found for user_id: {str_user_id}")
        # If the namespace doesn't exist, the user hasn't uploaded a video
        return None
    
    print(f"Namespace found for user_id: {str_user_id}")
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Create and return the PineconeVectorStore
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=str_user_id
    )

def query_pinecone(question, pinecone_store, namespace, chat_history):
    chat_history = truncate_chat_history(chat_history, max_tokens=5000)
    
    #retriever = pinecone_store.as_retriever(namespace=namespace, top_k=3)

    #context_documents = retriever.invoke(question)
    context_documents = pinecone_store.similarity_search(query=question, k=3, namespace=namespace)
    context = ' '.join([doc.page_content for doc in context_documents])
    
    history_context = "\n".join([f"User: {entry['question']}\nGPT-4: {entry['response']}" for entry in chat_history])
    full_context = f"{history_context}\n{context}"
    
    print(f"Retrieved context: '{context_documents}'")
    print(f"joined context: '{context}'")
    #print(f"Full context with history: '{full_context}'")
    
    chain = prompt | model | parser
    response = chain.invoke({
        "context": full_context,
        "question": question
    })
    return response

def summarize_with_gpt(summary):
    model = ChatGroq(temperature=0, model="llama3-8b-8192")
    template = """
        #Explain the following youtube transcript in a concise manner that highlights all the key point. 

        Context: {context}

        """

    prompt = ChatPromptTemplate.from_template(template)
    #question = "Explain the following youtube transcript in a concise manner that highlights all the key point." 
    chain = prompt | model | parser
    gpt_summary = chain.invoke({
        "context": summary
    })
    return gpt_summary