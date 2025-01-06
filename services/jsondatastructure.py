from pydantic import BaseModel, Field

class VOC(BaseModel):
    project_name: str = Field(description="Extracted project name")
    RICEF_id: str = Field(description="Generated or extracted RICEF ID")
    client_name: str = Field(description="Extracted client name")
    
    # Voice of Customer Section
    Voice_Of_Customer_WHAT_Functional_Description: str = Field(
        description="Voice of Customer - WHAT: Generate a client-centered question about the essential functions and capabilities required of the AI solution. For example, 'What are the essential functions and capabilities this AI solution should have to effectively address our business problem?'"
    )
    Voice_Of_Customer_WHY_Business_Benefit_Need: str = Field(
        description="Voice of Customer - WHY: Generate a question asking why this AI solution is necessary and what specific business benefits it provides. For example, 'What business benefits will this solution provide, and what risks or inefficiencies might arise if this solution is not in place?'"
    )
    Voice_Of_Customer_WHO_WHERE: str = Field(
        description="Voice of Customer - WHO/WHERE: Generate a question identifying the primary users of the AI solution, including departments, teams, or roles. For example, 'Who will be the primary users of this solution, and which departments or organizational units will benefit the most?'"
    )
    Voice_Of_Customer_WHEN: str = Field(
        description="Voice of Customer - WHEN: Generate a question to define how frequently and at what times the solution will be used. For example, 'How often will this solution need to be used, and are there specific times or intervals at which it must operate?'"
    )
    Voice_Of_Customer_HOW_Input: str = Field(
        description="Voice of Customer - HOW (Input): Generate a question specifying the necessary input data for the AI solution to work effectively. For example, 'What specific data inputs are necessary for this solution, and which fields or data sources are critical for achieving accurate results?'"
    )
    Voice_Of_Customer_HOW_Process: str = Field(
        description="Voice of Customer - HOW (Process): Generate a question to clarify how the AI solution should process the input data. For example, 'What specific processes, analyses, or computations should the AI solution perform on the input data to produce meaningful results?'"
    )
    Voice_Of_Customer_HOW_Output: str = Field(
        description="Voice of Customer - HOW (Output): Generate a question about the expected format and presentation of the AI solution’s output. For example, 'What should the final output look like, and how should it be formatted or presented to best support our decision-making needs?'"
    )






class ROC(BaseModel):
    
    # Functional Design Section
    project_name: str = Field(description="Extracted project name")
    RICEF_id: str = Field(description="Generated or extracted RICEF ID")
    client_name: str = Field(description="Extracted client name")

    alternatives_considered: str = Field(description="A listing of the various alternative approaches that were considered.")
    agreed_upon_approach: str = Field(description="Which alternative was selected?")
    
    # Functional Description Section
    functional_description: str = Field(
        description="Short Description of the required interface. What functionality is needed?"
    )
    business_benefit_need: str = Field(
        description="Short Description of why the interface is needed, and the impact if the interface is not implemented."
    )
    
    # Additional Section
    important_assumptions: str = Field(description="Important assumptions considered during the decision-making process.")
    additional_comments: str = Field(description="Any additional information considered during the decision-making process.")
    




class FD(BaseModel):

    # Functional Design Section
    project_name: str = Field(description="Extracted project name")
    RICEF_id: str = Field(description="Generated or extracted RICEF ID")
    client_name: str = Field(description="Extracted client name")

    Functional_Design_Process: str = Field(
        description="Functional Design - Process: Generated or extracted process flow for the functional design."
    )
    Functional_Design_Interface_Direction: str = Field(
        description="Functional Design - Interface Direction: Direction of data flow (to/from or bi-directional with SAP)."
    )
    Functional_Design_Error_Handling: str = Field(
        description="Functional Design - Error Handling: Generated or extracted error-handling owner definition and business needs."
    )
    Functional_Design_Frequency: str = Field(
        description="Functional Design - Frequency: Frequency at which the report will be run."
    )
    Functional_Design_Data_Volume: str = Field(
        description="Functional Design - Data Volume: Estimated data volume for the report."
    )
    Functional_Design_Security_Requirements: str = Field(
        description="Functional Design - Security Requirements: Security requirements requiring explicit authorization checks or special processing."
    )
    Functional_Design_Data_Sensitivity: str = Field(
        description="Functional Design - Data Sensitivity: Sensitivity of data, including level of restrictions."
    )
    Functional_Design_Unit_Testing: str = Field(
        description="Functional Design - Unit Testing: Information for unit testing scenarios, instructions, test data, and expected results."
    )
    Functional_Design_Additional_Comments: str = Field(
        description="Functional Design - Additional Comments: Additional information for functional design."
    )
    Functional_Design_Rework_Log: str = Field(
        description="Functional Design - Rework Log: Rework log containing previous version(s) of the section."
    )



class TD(BaseModel):

    # Technical Design Section
    project_name: str = Field(description="Extracted project name")
    RICEF_id: str = Field(description="Generated or extracted RICEF ID")
    client_name: str = Field(description="Extracted client name")
    Technical_Design_Design_Points: str = Field(
        description="Technical Design - Design Points: Design points for clear definition, including calculations, formulas, and performance recommendations."
    )
    Technical_Design_Special_Configuration_Settings: str = Field(
        description="Technical Design - Special Configuration Settings: Special configuration settings or temporary prerequisites."
    )
    Technical_Design_Outbound_Definition: str = Field(
        description="Technical Design - Outbound Definition: Outbound file(s) structure and format details."
    )
    Technical_Design_Target_Environment: str = Field(
        description="Technical Design - Target Environment: Target environment where data will be sent and any specific requirements."
    )
    Technical_Design_Starting_Transaction: str = Field(
        description="Technical Design - Starting Transaction: Starting transaction or application name."
    )
    Technical_Design_Triggering_Events: str = Field(
        description="Technical Design - Triggering Events: SAP business process event that triggers the report."
    )
    Technical_Design_Data_Transformation_Process: str = Field(
        description="Technical Design - Data Transformation Process: Data transformation process within SAP or middleware."
    )
    Technical_Design_Data_Transfer_Process: str = Field(
        description="Technical Design - Data Transfer Process: Description of data transfer process to SAP."
    )
    Technical_Design_Data_Format: str = Field(
        description="Technical Design - Data Format: Format of data (XML, EDI, Flat File, etc.)."
    )
    Technical_Design_Error_Handling: str = Field(
        description="Technical Design - Error Handling: Technical error handling components and owner definition."
    )
    Technical_Design_Additional_Process_Requirements: str = Field(
        description="Technical Design - Additional Process Requirements: Additional process requirements."
    )
    Technical_Design_Inbound_Definition: str = Field(
        description="Technical Design - Inbound Definition: Inbound file structure and format."
    )
    Technical_Design_Source_Environment: str = Field(
        description="Technical Design - Source Environment: Origin of data from an external system."
    )
    Technical_Design_Receiving_Transaction: str = Field(
        description="Technical Design - Receiving Transaction: Receiving transaction/application, whether it is new or existing."
    )
    Technical_Design_Rework_Log: str = Field(
        description="Technical Design - Rework Log: Rework log containing previous versions for technical design."
    )
