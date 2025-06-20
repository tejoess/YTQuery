from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    return None

def get_transcript(video_url):
    try:
        video_id = get_video_id(video_url)
        if not video_id:
            return "Error: Invalid YouTube URL"
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript_list])
    except Exception as e:
        return f"Error: {str(e)}"

def text_splitting(text):
    if not text:
        return []
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

def create_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    documents = [Document(page_content=chunk) for chunk in chunks]
    return FAISS.from_documents(documents, embeddings)

def create_retriever(vector_store, query):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    return retriever.invoke(query)

def create_chat_model(results, query, history):
    

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a YouTube Transcript QA bot. Only answer from transcript. If not found, say: 'The context does not contain the answer.'"),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("Transcript: {context}\n\nQuestion: {question}")
    ])

    # Ensure the context is built from valid results
    context = "\n\n".join([doc.page_content for doc in results if doc.page_content.strip()])
    print(prompt)
    # Validation
    if not context or not query.strip():
        return "Please provide the transcript and the question."

    # Make sure history is a list
    if history is None:
        history = []

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "context": context,
        "question": query.strip(),
        "history": history
    })

