import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from services.jsondatastructure import VOC, FD, TD, ROC

def openmodle(prompt, client_name):
    # Load the environment variables from the .env file
    load_dotenv()

    # Retrieve the API key from the environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    # Initialize the Groq chat model
    model = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

    # Determine the parser and template based on the query type
    if "VOC" in prompt:
        pydantic_object = VOC
        section_title = "**Voice of Customer Section**"
        fields = [
            "WHAT (Functional Description)",
            "WHY (Business Benefit/Need)",
            "WHO/WHERE",
            "WHEN",
            "HOW - Input",
            "HOW - Process",
            "HOW - Output",
            "Additional Comments",
        ]

    # For generating a prompt based on the class structure:
    elif "ROC" in prompt:
        pydantic_object = ROC
        section_title = "**Interface Decision Section**"
        fields = [
            "Alternatives Considered",
            "Agreed Upon Approach",
            "Functional Description",
            "Business Benefit/Need",
            "Important Assumptions",
            "Additional Comments",
        ]
    elif "FD" in prompt:
        pydantic_object = FD
        section_title = "**Functional Design Section**"
        fields = [
            "Process",
            "Interface Direction",
            "Error Handling",
            "Frequency",
            "Data Volume",
            "Security Requirements",
            "Data Sensitivity",
            "Unit Testing",
            "Additional Comments",
            "Rework Log",
        ]
    elif "TD" in prompt:
        pydantic_object = TD
        section_title = "**Technical Design Section**"
        fields = [
            "Design Points",
            "Special Configuration Settings",
            "Outbound Definition",
            "Target Environment",
            "Starting Transaction/Application",
            "Triggering Events",
            "Data Transformation Process",
            "Data Transfer Process",
            "Data Format",
            "Error Handling",
            "Additional Process Requirements",
            "Inbound Definition",
            "Source Environment",
            "Receiving Transaction/Application",
            "Rework Log",
        ]
    else:
        raise ValueError("Invalid business requirement query. Must contain 'VOC', 'FD', or 'TD'.")

    # Set up the parser
    parser = JsonOutputParser(pydantic_object=pydantic_object)

    # Define the prompt template
    template = (
        "Using the provided client business requirement, generate a complete RICEF form with detailed responses for the following fields. "
        "All fields must be filled; no field should be left blank or marked as 'to be determined'. Additionally, "
        "the client's name must be explicitly taken from the provided input prompt.\n\n"
        "{format_instructions}\n\n"
        f"- {section_title}:\n"
        + "\n".join([f"   - {field}" for field in fields])
        + "\n\nClient Name: {client_name}\n\nClient Business Requirement:\n{client_business_requirement}"
    )

    prompt = PromptTemplate(
        template=template,
        input_variables=["client_business_requirement", "client_name"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create and invoke the chain
    chain = prompt | model | parser
    response = chain.invoke({"client_business_requirement": prompt, "client_name": client_name})
    
    return response
