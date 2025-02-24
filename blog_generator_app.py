import os
import streamlit as st
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Define State
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# Initialize Language Model
model = ChatGroq(model="Gemma2-9b-It", temperature=0.7)

# Function to create LangGraph workflow
def make_blog_generation_graph():
    graph_workflow = StateGraph(State)

    def generate_title(state):
        prompt_1 = SystemMessage(content="As an experienced writer, generate one blog title.")
        return {"messages": [model.invoke([prompt_1] + state["messages"])]}

    def generate_content(state):
        prompt_2 = SystemMessage(content="As an experienced content creator, write a blog with a 500-word limit in 4 paragraphs.")
        return {"messages": [model.invoke([prompt_2] + state["messages"])]}

    graph_workflow.add_node("title_generation", generate_title)
    graph_workflow.add_node("content_generation", generate_content)
    
    graph_workflow.add_edge("title_generation", "content_generation")
    graph_workflow.add_edge("content_generation", END)
    graph_workflow.add_edge(START, "title_generation")

    return graph_workflow.compile()

# Streamlit UI
st.title("📝 AI Blog Generator")
st.write("Enter a topic below, and AI will generate a blog title and content for you!")

# User Input
topic = st.text_input("Enter a blog topic:", placeholder="Generative AI")

if st.button("Generate Blog"):
    if topic:
        st.write("⏳ Generating blog... Please wait.")

        # Initialize the blog generation agent
        blog_agent = make_blog_generation_graph()
        initial_state = State(messages=[HumanMessage(content=topic)])

        # Initialize placeholders for streaming output
        title_placeholder = st.empty()
        content_placeholder = st.empty()

        # Stream output step-by-step
        generated_title = ""
        generated_content = ""

        for output in blog_agent.stream(initial_state):
            for key, value in output.items():
                message_text = value["messages"][0].content

                if key == "title_generation":
                    generated_title = message_text
                    title_placeholder.markdown(f"### 🔥 Blog Title\n**{generated_title}**")

                if key == "content_generation":
                    generated_content = message_text
                    content_placeholder.markdown(f"### 📜 Blog Content\n{generated_content}")

        # Final display if streaming fails
        if not generated_title:
            title_placeholder.markdown("### ❌ Failed to generate title.")
        if not generated_content:
            content_placeholder.markdown("### ❌ Failed to generate blog content.")
    else:
        st.warning("⚠️ Please enter a topic before generating the blog.")
