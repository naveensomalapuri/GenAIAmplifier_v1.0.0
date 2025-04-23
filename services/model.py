import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from services.jsondatastructure import VOC, FD, TD, ROC





# -*- coding: utf-8 -*-
"""
Gen AI Amplifier Structured Output
===================================
This script demonstrates the use of the Tavily Search tool along with LangGraph,
Langsmith, and LangChain integrations to create a conversational agent with
structured output for functional design requirements.

API keys are loaded from a .env file. If the keys are not found, the user
will be prompted for the missing keys.

Original Notebook:
    https://colab.research.google.com/drive/1r2y-uIRG4VK0SZpE-196LwODAtJxvk3w
"""

# ------------------------------------------------------------------------------
# 1. Install Dependencies (if not already installed)
# ------------------------------------------------------------------------------
# !pip install langgraph langsmith langchain langchain_groq langchain_community python-dotenv

# ------------------------------------------------------------------------------
# 2. Import Statements
# ------------------------------------------------------------------------------
# Standard Library imports
import os
import getpass

# Third-Party Imports
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
# from IPython.display import Image, display

# LangChain, LangGraph, and related Imports
from langchain_tavily import TavilySearch
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage


def openmodel(client_business_requirement, client_name):
    # Google Colab specific import for handling user data storage (if needed)
    # In this updated version, we use the .env file for keys.
    # from google.colab import userdata

    # ------------------------------------------------------------------------------
    # 3. Load Environment Variables from .env File
    # ------------------------------------------------------------------------------
    # Load variables from a .env file located in the same directory.
    load_dotenv()

    # Retrieve the Tavily API key from the environment variables
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key is None:
        raise ValueError("TAVILY_API_KEY not found in the environment. Please add it to your .env file.")

    # Now you can use tavily_api_key as needed, for example:
    os.environ["TAVILY_API_KEY"] = tavily_api_key


    # ------------------------------------------------------------------------------
    # 4. Initialize the Tavily Search Tool
    # ------------------------------------------------------------------------------
    # Create an instance of the TavilySearch tool with the desired parameters.
    tool = TavilySearch(
        max_results=5,
        topic="general",
        search_depth="advanced",
        # Optional parameters (uncomment if necessary):
        # include_answer=False,
        # include_raw_content=False,
        # include_images=False,
        # include_image_descriptions=False,
        # time_range="day",
        # include_domains=None,
        # exclude_domains=None
    )
    # The tool can be invoked as needed (e.g., tool.invoke({"query": "your query"})).

    # ------------------------------------------------------------------------------
    # 5. Define the Structured Model for Functional Design Requirements
    # ------------------------------------------------------------------------------

    
    if "VOC" in client_business_requirement:
        Pydantic_Object = VOC
    elif "ROC" in client_business_requirement:
        Pydantic_Object = ROC
    elif "FD" in client_business_requirement:
        Pydantic_Object = FD
    elif "TD" in client_business_requirement:
        Pydantic_Object = TD
    else:
        # If none of the expected keywords are found, raise an error.
        raise ValueError("Invalid business requirement query. Must contain 'VOC', 'ROC', 'FD', or 'TD'.")

    # ------------------------------------------------------------------------------
    # 6. Define the Agent State for the Conversational Workflow
    # ------------------------------------------------------------------------------
    class AgentState(MessagesState):
        """
        Represents the current conversation state.
        Inherits a list of chat messages and includes a final structured response.
        """
        final_response: Pydantic_Object

    # ------------------------------------------------------------------------------
    # 7. Initialize the Chat Model and Bind Tools
    # ------------------------------------------------------------------------------
    # Retrieve the GROQ API key from environment variables.
    groq_api_key = os.environ.get("GROQ_API_KEY")
    # Initialize the ChatGroq model with the provided API key and specific model name.
    model = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

    # Bind the TavilySearch tool to the chat model.
    model_with_tools = model.bind_tools([tool])
    # Configure the model to return structured output following the Pydantic_Object model.
    model_with_structured_output = model.with_structured_output(Pydantic_Object)

    # ------------------------------------------------------------------------------
    # 8. Define Functions for the Conversational Workflow
    # ------------------------------------------------------------------------------
    def call_model(state: AgentState):
        """
        Invokes the chat model using the current list of messages in the conversation state.
        
        Args:
            state (AgentState): The current conversation state.
            
        Returns:
            dict: A dictionary containing a new list of messages from the model.
        """
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def respond(state: AgentState):
        """
        Generates the final structured response.
        
        Converts a previous tool response into a HumanMessage and invokes the model to produce the final output.
        
        Args:
            state (AgentState): The current conversation state.
            
        Returns:
            dict: A dictionary containing the final structured response.
        """
        response = model_with_structured_output.invoke(
            [HumanMessage(content=state["messages"][-2].content)]
        )
        return {"final_response": response}

    def should_continue(state: AgentState):
        """
        Determines if the workflow should continue tool invocation or generate the final response.
        
        Args:
            state (AgentState): The conversation state.
        
        Returns:
            str: "continue" if tool calls exist; otherwise "respond".
        """
        messages = state["messages"]
        last_message = messages[-1]
        return "respond" if not last_message.tool_calls else "continue"

    # ------------------------------------------------------------------------------
    # 9. Build the StateGraph Workflow
    # ------------------------------------------------------------------------------
    workflow = StateGraph(AgentState)

    # Define nodes representing stages of the workflow.
    workflow.add_node("agent", call_model)
    workflow.add_node("respond", respond)
    workflow.add_node("tools", ToolNode([tool]))

    # Set the entry point to the workflow.
    workflow.set_entry_point("agent")

    # Conditional edge based on whether to invoke a tool or to generate a final response.
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "respond": "respond",
        },
    )

    # Loop back to the agent node after using a tool.
    workflow.add_edge("tools", "agent")
    # Final node connecting to the end of the workflow.
    workflow.add_edge("respond", END)
    graph = workflow.compile()

    # ------------------------------------------------------------------------------
    # 10. (Optional) Display the Workflow Graph
    # ------------------------------------------------------------------------------
    # try:
    #     display(Image(graph.get_graph().draw_mermaid_png()))
    # except Exception:
    #     pass

    # ------------------------------------------------------------------------------
    # 11. Invoke the Workflow with User Input
    # ------------------------------------------------------------------------------
    # Prompt for user input (query or voice of the customer).
    Human_Input = client_business_requirement
    answer = graph.invoke(input={"messages": [("human", Human_Input)]})["final_response"]

    # Print the final structured response.
    print("\nStructured Final Response:")
    print(answer)

    # Optionally, convert the structured response to a dictionary.
    answer_dict = answer.dict()
    print("\nResponse as a Dictionary:")
    print(answer_dict)
    return answer_dict



# def openmodel(client_business_requirement, client_name):
#     """
#     Generates a RICEF form based on the provided client business requirement and client name.
    
#     This function examines the 'client_business_requirement' to determine which data structure 
#     (VOC, ROC, FD, or TD) to use. It then constructs a prompt template and invokes a chain of 
#     operations that include the chat model and an output parser to generate the final response.
    
#     Parameters:
#         client_business_requirement (str): The detailed business requirement provided by the client.
#         client_name (str): The name of the client.
    
#     Returns:
#         response: The processed output from the chain after invoking the model and parser.
#     """
#     # Load environment variables from the .env file to access sensitive data like API keys.
#     load_dotenv()

#     # Retrieve the GROQ API key from the environment variables.
#     groq_api_key = os.getenv("GROQ_API_KEY")
#     if not groq_api_key:
#         raise ValueError("GROQ_API_KEY is not set in the environment.")

#     # Initialize the ChatGroq model with a specific model name and the retrieved API key.
#     model = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

#     # Determine the pydantic object, section title, and fields based on keywords found in the business requirement.
#     if "VOC" in client_business_requirement:
#         # VOC (Voice of Customer) section details.
#         pydantic_object = VOC
#         section_title = "**Voice of Customer Section**"
#         fields = [
#             "WHAT (Functional Description)",
#             "WHY (Business Benefit/Need)",
#             "WHO/WHERE",
#             "WHEN",
#             "HOW - Input",
#             "HOW - Process",
#             "HOW - Output",
#             "Additional Comments",
#         ]
#     elif "ROC" in client_business_requirement:
#         # ROC (Interface Decision) section details.
#         pydantic_object = ROC
#         section_title = "**Interface Decision Section**"
#         fields = [
#             "Alternatives Considered",
#             "Agreed Upon Approach",
#             "Functional Description",
#             "Business Benefit/Need",
#             "Important Assumptions",
#             "Additional Comments",
#         ]
#     elif "FD" in client_business_requirement:
#         # FD (Functional Design) section details.
#         pydantic_object = FD
#         section_title = "**Functional Design Section**"
#         # fields = [
#         #     "Process",
#         #     "Interface Direction",
#         #     "Error Handling",
#         #     "Frequency",
#         #     "Data Volume",
#         #     "Security Requirements",
#         #     "Data Sensitivity",
#         #     "Unit Testing",
#         #     "Additional Comments",
#         #     "Rework Log",
#         # ]
#         fields = [
#             "Process",
#             "Interface Direction",
#             "Error Handling",
#             "Frequency",
#             "Data Volume",
#             "Security Requirements",
#             "Data Sensitivity",
#             "Unit Testing",
#             "Additional Comments",
#             "Rework Log",
#             # New fields added from:
#             # "Functional_Design_reference_transactions_tables_programs"
#             # "Functional_Design_input_selection_criteria"
#             # "Functional_Design_solution_format"
#             # "Functional_Design_output_format_details"
#             # "Functional_Design_barcode_requirements"
#             # "Functional_Design_paper_requirements"
#             # "Functional_Design_logo_requirements"
#             # "Functional_Design_software_requirements"
#             # "Functional_Design_printer_requirements"
#             # "Functional_Design_output_type_application"
#             "Reference transactions tables programs",
#             "Input selection criteria",
#             "Solution format",
#             "Output format details",
#             "Barcode requirements",
#             "Paper requirements",
#             "Logo requirements",
#             "Software requirements",
#             "Printer requirements",
#             "Output type application",
#         ]

#     elif "TD" in client_business_requirement:
#         # TD (Technical Design) section details.
#         pydantic_object = TD
#         section_title = "**Technical Design Section**"
#         fields = [
#             "Design Points",
#             "Special Configuration Settings",
#             "Outbound Definition",
#             "Target Environment",
#             "Starting Transaction/Application",
#             "Triggering Events",
#             "Data Transformation Process",
#             "Data Transfer Process",
#             "Data Format",
#             "Error Handling",
#             "Additional Process Requirements",
#             "Inbound Definition",
#             "Source Environment",
#             "Receiving Transaction/Application",
#             "Rework Log",
#         ]
#     else:
#         # If none of the expected keywords are found, raise an error.
#         raise ValueError("Invalid business requirement query. Must contain 'VOC', 'ROC', 'FD', or 'TD'.")

#     # Initialize the output parser with the chosen pydantic data structure.
#     parser = JsonOutputParser(pydantic_object=pydantic_object)

#     # Create a prompt template that includes format instructions and a list of required fields.
#     # Notice the use of doubled curly braces to leave placeholders intact for the PromptTemplate.
#     template = (
#         "Using the provided client business requirement, generate a complete RICEF form with detailed responses for the following fields. "
#         "All fields must be filled; no field should be left blank or marked as 'to be determined'. Additionally, "
#         "the client's name must be explicitly taken from the provided input prompt.\n\n"
#         "{format_instructions}\n\n"
#         f"- {section_title}:\n" +
#         "\n".join([f"   - {field}" for field in fields]) +
#         "\n\nClient Name: {{client_name}}\n\nClient Business Requirement:\n{{client_business_requirement}}"
#     )

#     # Create the PromptTemplate instance using the defined template and expected input variables.
#     prompt_template = PromptTemplate(
#         template=template,
#         input_variables=["client_business_requirement", "client_name"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#     )

#     # Compose the chain with the prompt template, the model, and the parser.
#     # The '|' operator is used to link these components.
#     chain = prompt_template | model | parser

#     # Invoke the chain with the provided parameters to generate a response.
#     response = chain.invoke({
#         "client_business_requirement": client_business_requirement,
#         "client_name": client_name
#     })
    
#     # Return the final generated response.
#     return response







def openmodel_regeneration(client_business_requirement, client_name, previous_response, current_response, index_value):
    # Google Colab specific import for handling user data storage (if needed)
    # In this updated version, we use the .env file for keys.
    # from google.colab import userdata

    # ------------------------------------------------------------------------------
    # 3. Load Environment Variables from .env File
    # ------------------------------------------------------------------------------
    # Load variables from a .env file located in the same directory.
    load_dotenv()

    # Retrieve the Tavily API key from the environment variables
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key is None:
        raise ValueError("TAVILY_API_KEY not found in the environment. Please add it to your .env file.")

    # Now you can use tavily_api_key as needed, for example:
    os.environ["TAVILY_API_KEY"] = tavily_api_key


    # ------------------------------------------------------------------------------
    # 4. Initialize the Tavily Search Tool
    # ------------------------------------------------------------------------------
    # Create an instance of the TavilySearch tool with the desired parameters.
    tool = TavilySearch(
        max_results=5,
        topic="general",
        search_depth="advanced",
        # Optional parameters (uncomment if necessary):
        # include_answer=False,
        # include_raw_content=False,
        # include_images=False,
        # include_image_descriptions=False,
        # time_range="day",
        # include_domains=None,
        # exclude_domains=None
    )
    # The tool can be invoked as needed (e.g., tool.invoke({"query": "your query"})).

    # ------------------------------------------------------------------------------
    # 5. Define the Structured Model for Functional Design Requirements
    # ------------------------------------------------------------------------------

    
    if index_value == 0:
        Pydantic_Object = VOC
    elif index_value == 1:
        Pydantic_Object = ROC
    elif index_value == 2:
        Pydantic_Object = FD
    elif index_value == 3:
        Pydantic_Object = TD
    else:
        # If none of the expected keywords are found, raise an error.
        raise ValueError("Invalid business requirement query. Must contain 'VOC', 'ROC', 'FD', or 'TD'.")

    # ------------------------------------------------------------------------------
    # 6. Define the Agent State for the Conversational Workflow
    # ------------------------------------------------------------------------------
    class AgentState(MessagesState):
        """
        Represents the current conversation state.
        Inherits a list of chat messages and includes a final structured response.
        """
        final_response: Pydantic_Object

    # ------------------------------------------------------------------------------
    # 7. Initialize the Chat Model and Bind Tools
    # ------------------------------------------------------------------------------
    # Retrieve the GROQ API key from environment variables.
    groq_api_key = os.environ.get("GROQ_API_KEY")
    # Initialize the ChatGroq model with the provided API key and specific model name.
    model = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

    # Bind the TavilySearch tool to the chat model.
    model_with_tools = model.bind_tools([tool])
    # Configure the model to return structured output following the Pydantic_Object model.
    model_with_structured_output = model.with_structured_output(Pydantic_Object)

    # ------------------------------------------------------------------------------
    # 8. Define Functions for the Conversational Workflow
    # ------------------------------------------------------------------------------
    def call_model(state: AgentState):
        """
        Invokes the chat model using the current list of messages in the conversation state.
        
        Args:
            state (AgentState): The current conversation state.
            
        Returns:
            dict: A dictionary containing a new list of messages from the model.
        """
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def respond(state: AgentState):
        """
        Generates the final structured response.
        
        Converts a previous tool response into a HumanMessage and invokes the model to produce the final output.
        
        Args:
            state (AgentState): The current conversation state.
            
        Returns:
            dict: A dictionary containing the final structured response.
        """
        response = model_with_structured_output.invoke(
            [HumanMessage(content=state["messages"][-2].content)]
        )
        return {"final_response": response}

    def should_continue(state: AgentState):
        """
        Determines if the workflow should continue tool invocation or generate the final response.
        
        Args:
            state (AgentState): The conversation state.
        
        Returns:
            str: "continue" if tool calls exist; otherwise "respond".
        """
        messages = state["messages"]
        last_message = messages[-1]
        return "respond" if not last_message.tool_calls else "continue"

    # ------------------------------------------------------------------------------
    # 9. Build the StateGraph Workflow
    # ------------------------------------------------------------------------------
    workflow = StateGraph(AgentState)

    # Define nodes representing stages of the workflow.
    workflow.add_node("agent", call_model)
    workflow.add_node("respond", respond)
    workflow.add_node("tools", ToolNode([tool]))

    # Set the entry point to the workflow.
    workflow.set_entry_point("agent")

    # Conditional edge based on whether to invoke a tool or to generate a final response.
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "respond": "respond",
        },
    )

    # Loop back to the agent node after using a tool.
    workflow.add_edge("tools", "agent")
    # Final node connecting to the end of the workflow.
    workflow.add_edge("respond", END)
    graph = workflow.compile()

    # ------------------------------------------------------------------------------
    # 10. (Optional) Display the Workflow Graph
    # ------------------------------------------------------------------------------
    # try:
    #     display(Image(graph.get_graph().draw_mermaid_png()))
    # except Exception:
    #     pass

    # ------------------------------------------------------------------------------
    # 11. Invoke the Workflow with User Input
    # ------------------------------------------------------------------------------
    # Prompt for user input (query or voice of the customer).
    Human_Input = "Client Business Requirement : " + client_business_requirement + "Privous Response : " + previous_response + "Current Response : " + current_response + "Based on the Client Business Requirement & Previous Response Enhance Current Response"
    print(Human_Input)
    answer = graph.invoke(input={"messages": [("human", Human_Input)]})["final_response"]

    # Print the final structured response.
    print("\nStructured Final Response:")
    print(answer)

    # Optionally, convert the structured response to a dictionary.
    answer_dict = answer.dict()
    print("\nResponse as a Dictionary:")
    print(answer_dict)
    return answer_dict




# def openmodel_regeneration(client_business_requirement, client_name, previous_response, current_response, index_value):
#     """
#     Regenerates an enhanced RICEF form response by considering previous and current responses.
    
#     This overloaded function uses an 'index_value' to determine which data structure to use:
#       - 0: VOC
#       - 1: ROC
#       - 2: FD
#       - 3: TD
#     The function builds a detailed prompt that incorporates the original business requirement, 
#     the previous response, and the current response, and then invokes the model to generate an enhanced output.
    
#     Parameters:
#         client_business_requirement (str): The original business requirement provided by the client.
#         client_name (str): The client's name.
#         previous_response (str): The response generated in a previous run.
#         current_response (str): The most recent response prior to regeneration.
#         index_value (int): A value from 0 to 3 that selects the appropriate data structure (VOC, ROC, FD, TD).
    
#     Returns:
#         response: The enhanced output from the chain after model and parser invocation.
#     """
#     # Load environment variables to access the GROQ API key.
#     load_dotenv()

#     # Retrieve the GROQ API key from environment variables.
#     groq_api_key = os.getenv("GROQ_API_KEY")
#     if not groq_api_key:
#         raise ValueError("GROQ_API_KEY is not set in the environment.")

#     # Initialize the ChatGroq model with the specific model name and API key.
#     model = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

#     # Select the appropriate pydantic object, section title, and fields based on the provided index_value.
#     if index_value == 0:
#         pydantic_object = VOC
#         section_title = "**Voice of Customer Section**"
#         fields = [
#             "WHAT (Functional Description)",
#             "WHY (Business Benefit/Need)",
#             "WHO/WHERE",
#             "WHEN",
#             "HOW - Input",
#             "HOW - Process",
#             "HOW - Output",
#             "Additional Comments",
#         ]
#     elif index_value == 1:
#         pydantic_object = ROC
#         section_title = "**Interface Decision Section**"
#         fields = [
#             "Alternatives Considered",
#             "Agreed Upon Approach",
#             "Functional Description",
#             "Business Benefit/Need",
#             "Important Assumptions",
#             "Additional Comments",
#         ]
#     elif index_value == 2:
#         pydantic_object = FD
#         section_title = "**Functional Design Section**"
#         # fields = [
#         #     "Process",
#         #     "Interface Direction",
#         #     "Error Handling",
#         #     "Frequency",
#         #     "Data Volume",
#         #     "Security Requirements",
#         #     "Data Sensitivity",
#         #     "Unit Testing",
#         #     "Additional Comments",
#         #     "Rework Log",
#         # ]
#         fields = [
#             "Process",
#             "Interface Direction",
#             "Error Handling",
#             "Frequency",
#             "Data Volume",
#             "Security Requirements",
#             "Data Sensitivity",
#             "Unit Testing",
#             "Additional Comments",
#             "Rework Log",
#             # New fields added from:
#             # "Functional_Design_reference_transactions_tables_programs"
#             # "Functional_Design_input_selection_criteria"
#             # "Functional_Design_solution_format"
#             # "Functional_Design_output_format_details"
#             # "Functional_Design_barcode_requirements"
#             # "Functional_Design_paper_requirements"
#             # "Functional_Design_logo_requirements"
#             # "Functional_Design_software_requirements"
#             # "Functional_Design_printer_requirements"
#             # "Functional_Design_output_type_application"
#             "Reference transactions tables programs",
#             "Input selection criteria",
#             "Solution format",
#             "Output format details",
#             "Barcode requirements",
#             "Paper requirements",
#             "Logo requirements",
#             "Software requirements",
#             "Printer requirements",
#             "Output type application",
#         ]

#     elif index_value == 3:
#         pydantic_object = TD
#         section_title = "**Technical Design Section**"
#         fields = [
#             "Design Points",
#             "Special Configuration Settings",
#             "Outbound Definition",
#             "Target Environment",
#             "Starting Transaction/Application",
#             "Triggering Events",
#             "Data Transformation Process",
#             "Data Transfer Process",
#             "Data Format",
#             "Error Handling",
#             "Additional Process Requirements",
#             "Inbound Definition",
#             "Source Environment",
#             "Receiving Transaction/Application",
#             "Rework Log",
#         ]
#     else:
#         # If index_value is not in the expected range, raise an error.
#         raise ValueError("Invalid index_value. Must be 0 for VOC, 1 for ROC, 2 for FD, or 3 for TD.")

#     # Set up the output parser with the selected pydantic object.
#     parser = JsonOutputParser(pydantic_object=pydantic_object)

#     # Construct an enhanced prompt template that includes the original business requirement, previous response,
#     # and current response. The template instructs the model to generate an enhanced response.
#     template = (
#         "Using the provided client business requirement, generate a complete RICEF form with detailed responses for the following fields. "
#         "All fields must be filled; no field should be left blank or marked as 'to be determined'. Additionally, "
#         "the client's name must be explicitly taken from the provided input prompt.\n\n"
#         "Previous Response is generated by the client problem. Now, the Current Response is generated based on the Previous Response, "
#         "but now, understanding the Current Response clearly, provide an enhanced new response based on the client problem, Previous Response, "
#         "and Current Response.\n\n"
#         "{format_instructions}\n\n"
#         f"- {section_title}:\n" +
#         "\n".join([f"   - {field}" for field in fields]) +
#         "\n\nClient Name: {{client_name}}\n\n"
#         "Client Business Requirement:\n{{client_business_requirement}}\n\n"
#         "Previous Response:\n{{previous_response}}\n\n"
#         "Current Response:\n{{current_response}}\n\n"
#     )

#     # Create a PromptTemplate instance with all required variables.
#     prompt_template = PromptTemplate(
#         template=template,
#         input_variables=["client_business_requirement", "client_name", "previous_response", "current_response"],
#         partial_variables={"format_instructions": parser.get_format_instructions()},
#     )

#     # Compose the chain that links the prompt template, the model, and the output parser.
#     chain = prompt_template | model | parser

#     # Invoke the chain with the provided parameters to generate the enhanced response.
#     response = chain.invoke({
#         "client_business_requirement": client_business_requirement,
#         "client_name": client_name,
#         "previous_response": previous_response,
#         "current_response": current_response
#     })
    
#     # Return the final enhanced response.
#     return response
