import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI and Groq chatbots
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize Groq chatbot
#llm = ChatGroq(model="Llama-3-70B-Tool-Use")
# Alternatively, use OpenAI's ChatGPT
llm = ChatOpenAI(model="gpt-4")

def get_youtube_transcript(video_url):
    try:
        # Extract Video ID from URL
        video_id = video_url.split("v=")[-1].split("&")[0]
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Convert transcript list to text
        transcript_text = "\n".join([entry["text"] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error: {str(e)}"

# Graph state
class State(TypedDict):
    video_url: str
    transcript: str
    blog: str
    review: str
    human_feedback: str

def transcript_generation(state: State) -> State:
    # Fetch transcript
    state["transcript"] = get_youtube_transcript(state["video_url"])
    return state

def blog_generation(state: State) -> State:
    if state.get("human_feedback"):
        state["blog"] = llm.invoke(
            f"Generate a blog post for the transcript below:\n{state['transcript']}\n"
            f"Consider the following feedback: {state['human_feedback']}"
        )
    else:
        state["blog"] = llm.invoke(
            f"Generate a blog post for the transcript below:\n{state['transcript']}"
        )
    return state

def review_generation(state: State) -> State:
    # Generate review
    state["review"] = llm.invoke(f"Generate a review for the blog post below:\n{state['blog']}")
    return state

def human_feedback1(state: State) -> State:
    feedback = interrupt("Please provide your feedback:")
    return {"human_feedback": feedback}

def should_continue(state: State) -> str:
    if state.get("human_feedback"):
        return "blogger"
    return END

# Initialize memory saver
memory = MemorySaver()

# Build the state graph
builder = StateGraph(State)
# Nodes
builder.add_node("transcriptor", transcript_generation)
builder.add_node("blogger", blog_generation)
builder.add_node("reviewer", review_generation)
builder.add_node("human_analyst_feedback", human_feedback1)
# Edges
builder.add_edge(START, "transcriptor")
builder.add_edge("transcriptor", "blogger")
builder.add_edge("blogger", "reviewer")
builder.add_edge("reviewer", "human_analyst_feedback")
builder.add_conditional_edges("human_analyst_feedback", should_continue, ["blogger", END])

# Compile the workflow with an interrupt before 'human_analyst_feedback'
workflow = builder.compile(interrupt_before=["human_analyst_feedback"], checkpointer=memory)

# Streamlit app
st.title("YouTube Blog Generator with Human Feedback")

# Input for YouTube video URL
video_url = st.text_input("Enter YouTube Video URL:")

if video_url:
    # Initialize the thread
    thread = {"configurable": {"thread_id": "1"}}
    # Run the workflow until the first interruption
    for event in workflow.stream({"video_url": video_url}, thread, stream_mode="values"):
        blog = event.get("blog", None)
        review = event.get("review", None)
        if blog and review:
            st.subheader("Generated Blog")
            st.markdown(blog.content)
            st.subheader("Blog Review")
            st.markdown(review.content)
            break

    # Collect human feedback
    user_feedback = st.text_area("Provide your feedback (optional):")

    if st.button("Submit Feedback"):
        if user_feedback:
            # Resume workflow with feedback
            final_state = workflow.invoke(Command(resume=user_feedback), thread)
        else:
            # Resume workflow without feedback
            final_state = workflow.invoke(Command(resume=""), thread)

        # Display the final blog content
        final_blog = final_state.get("blog")
        if final_blog:
            st.subheader("Final Blog Post")
            print("Final Blog Post:")
            st.markdown(final_blog.content)
        else:
            st.error("No blog content generated.")