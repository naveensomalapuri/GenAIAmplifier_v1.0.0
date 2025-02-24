import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from services.jsondatastructure import VOC, FD, TD, ROC


def openmodel(client_business_requirement, client_name):
    """
    Generates a RICEF form based on the provided client business requirement and client name.
    
    This function examines the 'client_business_requirement' to determine which data structure 
    (VOC, ROC, FD, or TD) to use. It then constructs a prompt template and invokes a chain of 
    operations that include the chat model and an output parser to generate the final response.
    
    Parameters:
        client_business_requirement (str): The detailed business requirement provided by the client.
        client_name (str): The name of the client.
    
    Returns:
        response: The processed output from the chain after invoking the model and parser.
    """
    # Load environment variables from the .env file to access sensitive data like API keys.
    load_dotenv()

    # Retrieve the GROQ API key from the environment variables.
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    # Initialize the ChatGroq model with a specific model name and the retrieved API key.
    model = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

    # Determine the pydantic object, section title, and fields based on keywords found in the business requirement.
    if "VOC" in client_business_requirement:
        # VOC (Voice of Customer) section details.
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
    elif "ROC" in client_business_requirement:
        # ROC (Interface Decision) section details.
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
    elif "FD" in client_business_requirement:
        # FD (Functional Design) section details.
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
    elif "TD" in client_business_requirement:
        # TD (Technical Design) section details.
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
        # If none of the expected keywords are found, raise an error.
        raise ValueError("Invalid business requirement query. Must contain 'VOC', 'ROC', 'FD', or 'TD'.")

    # Initialize the output parser with the chosen pydantic data structure.
    parser = JsonOutputParser(pydantic_object=pydantic_object)

    # Create a prompt template that includes format instructions and a list of required fields.
    # Notice the use of doubled curly braces to leave placeholders intact for the PromptTemplate.
    template = (
        "Using the provided client business requirement, generate a complete RICEF form with detailed responses for the following fields. "
        "All fields must be filled; no field should be left blank or marked as 'to be determined'. Additionally, "
        "the client's name must be explicitly taken from the provided input prompt.\n\n"
        "{format_instructions}\n\n"
        f"- {section_title}:\n" +
        "\n".join([f"   - {field}" for field in fields]) +
        "\n\nClient Name: {{client_name}}\n\nClient Business Requirement:\n{{client_business_requirement}}"
    )

    # Create the PromptTemplate instance using the defined template and expected input variables.
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["client_business_requirement", "client_name"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Compose the chain with the prompt template, the model, and the parser.
    # The '|' operator is used to link these components.
    chain = prompt_template | model | parser

    # Invoke the chain with the provided parameters to generate a response.
    response = chain.invoke({
        "client_business_requirement": client_business_requirement,
        "client_name": client_name
    })
    
    # Return the final generated response.
    return response


def openmodel_regeneration(client_business_requirement, client_name, previous_response, current_response, index_value):
    """
    Regenerates an enhanced RICEF form response by considering previous and current responses.
    
    This overloaded function uses an 'index_value' to determine which data structure to use:
      - 0: VOC
      - 1: ROC
      - 2: FD
      - 3: TD
    The function builds a detailed prompt that incorporates the original business requirement, 
    the previous response, and the current response, and then invokes the model to generate an enhanced output.
    
    Parameters:
        client_business_requirement (str): The original business requirement provided by the client.
        client_name (str): The client's name.
        previous_response (str): The response generated in a previous run.
        current_response (str): The most recent response prior to regeneration.
        index_value (int): A value from 0 to 3 that selects the appropriate data structure (VOC, ROC, FD, TD).
    
    Returns:
        response: The enhanced output from the chain after model and parser invocation.
    """
    # Load environment variables to access the GROQ API key.
    load_dotenv()

    # Retrieve the GROQ API key from environment variables.
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    # Initialize the ChatGroq model with the specific model name and API key.
    model = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

    # Select the appropriate pydantic object, section title, and fields based on the provided index_value.
    if index_value == 0:
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
    elif index_value == 1:
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
    elif index_value == 2:
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
    elif index_value == 3:
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
        # If index_value is not in the expected range, raise an error.
        raise ValueError("Invalid index_value. Must be 0 for VOC, 1 for ROC, 2 for FD, or 3 for TD.")

    # Set up the output parser with the selected pydantic object.
    parser = JsonOutputParser(pydantic_object=pydantic_object)

    # Construct an enhanced prompt template that includes the original business requirement, previous response,
    # and current response. The template instructs the model to generate an enhanced response.
    template = (
        "Using the provided client business requirement, generate a complete RICEF form with detailed responses for the following fields. "
        "All fields must be filled; no field should be left blank or marked as 'to be determined'. Additionally, "
        "the client's name must be explicitly taken from the provided input prompt.\n\n"
        "Previous Response is generated by the client problem. Now, the Current Response is generated based on the Previous Response, "
        "but now, understanding the Current Response clearly, provide an enhanced new response based on the client problem, Previous Response, "
        "and Current Response.\n\n"
        "{format_instructions}\n\n"
        f"- {section_title}:\n" +
        "\n".join([f"   - {field}" for field in fields]) +
        "\n\nClient Name: {{client_name}}\n\n"
        "Client Business Requirement:\n{{client_business_requirement}}\n\n"
        "Previous Response:\n{{previous_response}}\n\n"
        "Current Response:\n{{current_response}}\n\n"
    )

    # Create a PromptTemplate instance with all required variables.
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["client_business_requirement", "client_name", "previous_response", "current_response"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Compose the chain that links the prompt template, the model, and the output parser.
    chain = prompt_template | model | parser

    # Invoke the chain with the provided parameters to generate the enhanced response.
    response = chain.invoke({
        "client_business_requirement": client_business_requirement,
        "client_name": client_name,
        "previous_response": previous_response,
        "current_response": current_response
    })
    
    # Return the final enhanced response.
    return response
