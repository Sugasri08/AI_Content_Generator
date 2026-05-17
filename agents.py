from crewai import Agent, LLM
import os

 
groq_llm = LLM(
    model="groq/llama3-8b-8192",        
    api_key=os.environ.get("GROQ_API_KEY"),  # set in .env or terminal
    temperature=0.7,
    max_tokens=1024,
)


def content_researcher():
    return Agent(
        role="Content Researcher",

        goal="""
        Research trending and valuable information
        about the given topic.
        """,

        backstory="""
        You are an expert internet researcher who finds
        concise, useful and engaging insights quickly.
        """,

        llm=groq_llm,

        verbose=False
    )


def content_writer():
    return Agent(
        role="Content Writer",

        goal="""
        Create high-quality content in multiple formats.
        """,

        backstory="""
        You are a professional writer skilled in blogs,
        emails, captions, LinkedIn posts and scripts.
        """,

        llm=groq_llm,

        verbose=False
    )