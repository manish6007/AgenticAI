import os
import streamlit as st
from dotenv import load_dotenv
from typing_extensions import TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

load_dotenv()

# Set API Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(model="qwen-2.5-32b")

class State(TypedDict):
    code: str
    requirement: str
    feedback: str
    correct_or_not: str
    readme: str

# Schema for structured output
class Feedback(BaseModel):
    review: Literal["correct", "not correct"] = Field(
        description="Decide if the code is correct as per requirement or not."
    )
    feedback: str = Field(
        description="If the code is not as per requirement, provide feedback."
    )

reviewer = llm.with_structured_output(Feedback)

def llm_code_generator(requirement: str):
    response = llm.invoke(f"Write a code for the requirement: {requirement}, No preambles.")
    return response.content

def llm_code_reviewer(state: State):
    feedback = reviewer.invoke(f"Review the code {state['code']} for the requirement {state['requirement']}")
    return {"correct_or_not": feedback.review, "feedback": feedback.feedback}

def llm_generate_readme(code: str):
    response = llm.invoke(f"Generate a README documentation in markdown format for the following code: {code}")
    return response.content

# Streamlit UI
st.title("AI-Powered Code Generator & Reviewer")
requirement = st.text_area("Enter the requirement:")
if st.button("Generate Code"):
    generated_code = llm_code_generator(requirement)
    state = {"requirement": requirement, "code": generated_code, "feedback": "", "correct_or_not": "", "readme": ""}
    result = llm_code_reviewer(state)
    state.update(result)
    st.subheader("Generated Code:")
    st.code(state["code"], language="python")
    
    if state["correct_or_not"] == "not correct":
        st.error("Feedback: " + state["feedback"])
    else:
        st.success("The code is reviewed and can be used!")
        readme_content = llm_generate_readme(state["code"])
        st.subheader("Generated README:")
        st.markdown(readme_content, unsafe_allow_html=True)
