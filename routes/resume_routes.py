from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from services.resume_service import generate_resume, save_resume, get_all_resumes, view_resume
from models.resume_model import Resume
from pdfcrowd import HtmlToPdfClient
import os
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/create_resume")
async def show_form(request: Request):
    return templates.TemplateResponse("business_problem_form.html", {"request": request})



@router.post("/generate_response")
async def create_resume(client_problem: str = Form(...), client_name: str = Form(...)):
    # Log input values
    print(f"Received client_problem: {client_problem}")
    print(f"Received client_name: {client_name}")

    # Generate the resume
    generated_resume = generate_resume(client_problem, client_name)
    print(f"Generated resume: {generated_resume}")

    # Create a Resume instance (include client_name if the model requires it)
    resume = Resume(client_problem=client_problem, generated_resume=generated_resume, client_name=client_name)

    # Save to the database
    resume_dict = resume.dict()
    resume_id = save_resume(resume_dict)

    if resume_id:
        print(f"Resume saved with ID: {resume_id}")
        return RedirectResponse(url="/", status_code=303)
    else:
        raise HTTPException(status_code=500, detail="Failed to save resume")

"""
@router.get("/")
async def list_resumes(request: Request):
    resumes = get_all_resumes()
    return templates.TemplateResponse("resume_list.html", {"request": request, "resumes": resumes})"""

@router.get("/", response_class=HTMLResponse)
async def get_app(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})



@router.get("/section1.html", response_class=HTMLResponse)
async def open_section1(request: Request):
    # Extract query parameters from the request URL
    query_params = request.query_params

    # You can access each parameter like this:
    ricefw = query_params.get("ricefw")
    customer = query_params.get("customer")
    ricefw_number = query_params.get("ricefw-number")
    module = query_params.get("module")
    specification = query_params.get("specification")
    description = query_params.get("description")
    related_ricefw = query_params.get("related-ricefw")
    created_by = query_params.get("created-by")
    document_date = query_params.get("document-date")
    completion_date = query_params.get("completion-date")
    client_owner_name = query_params.get("client-owner-name")
    client_owner_company = query_params.get("client-owner-company")
    client_owner_email = query_params.get("client-owner-email")
    client_owner_phone = query_params.get("client-owner-phone")
    functional_owner_name = query_params.get("functional-owner-name")
    functional_owner_company = query_params.get("functional-owner-company")
    functional_owner_email = query_params.get("functional-owner-email")
    functional_owner_phone = query_params.get("functional-owner-phone")
    technical_owner_name = query_params.get("technical-owner-name")
    technical_owner_company = query_params.get("technical-owner-company")
    technical_owner_email = query_params.get("technical-owner-email")
    technical_owner_phone = query_params.get("technical-owner-phone")
    developer_name = query_params.get("developer-name")
    developer_company = query_params.get("developer-company")
    developer_email = query_params.get("developer-email")
    developer_phone = query_params.get("developer-phone")
    fileText = query_params.get("fileText")
    
    # Prepare data to pass to the template
    params_data = {
        "ricefw": ricefw,
        "customer": customer,
        "ricefw_number": ricefw_number,
        "module": module,
        "specification": specification,
        "description": description,
        "related_ricefw": related_ricefw,
        "created_by": created_by,
        "document_date": document_date,
        "completion_date": completion_date,
        "client_owner_name": client_owner_name,
        "client_owner_company": client_owner_company,
        "client_owner_email": client_owner_email,
        "client_owner_phone": client_owner_phone,
        "functional_owner_name": functional_owner_name,
        "functional_owner_company": functional_owner_company,
        "functional_owner_email": functional_owner_email,
        "functional_owner_phone": functional_owner_phone,
        "technical_owner_name": technical_owner_name,
        "technical_owner_company": technical_owner_company,
        "technical_owner_email": technical_owner_email,
        "technical_owner_phone": technical_owner_phone,
        "developer_name": developer_name,
        "developer_company": developer_company,
        "developer_email": developer_email,
        "developer_phone": developer_phone,
        "fileText": fileText
    }

    resumes = get_all_resumes()

    # Return the template with the data
    return templates.TemplateResponse("section1.html", {"request": request, "params_data": params_data, "resumes":resumes})



@router.post("/section2", response_class=HTMLResponse)  # Changed to POST
async def open_section(request: Request):

    try:
        data = await request.json()  # Expecting a JSON body for POST request
        print("Received data:", data)

        resumes = get_all_resumes()  # Assuming this function retrieves all resumes

        # Return the template with the data
        return templates.TemplateResponse("section2.html", {"request": request, "data": data, "resumes": resumes})

    except Exception as e:
        print("Error:", e)
        return JSONResponse(content={"error": "Failed to process data."}, status_code=500)



@router.get("/resume_view/{resume_name}")
async def view(resume_name: str, request: Request):
    # Call the synchronous function to retrieve the resume data
    print(resume_name)
    resume = view_resume(resume_name)
    print(resume)
    if isinstance(resume, list):
        print("if block of view excuting")
        return templates.TemplateResponse("riceffile.html", {"request": request, "resume": resume})
    else:
        raise HTTPException(status_code=404, detail="RICEF not found")



# new code 
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse
from docxtpl import DocxTemplate
import io



@router.get("/resume_download/{resume_name}")
async def download_pdf(resume_name: str, request: Request):
    # Retrieve the resume data
    resume = view_resume(resume_name)
    if isinstance(resume, list):
        # Load Word template and populate with data
        template = DocxTemplate("templates/template.docx")
        template.render({"resume": resume})

        # Save to a BytesIO stream instead of file
        byte_io = io.BytesIO()
        template.save(byte_io)
        byte_io.seek(0)

        # Return the Word document as a downloadable file
        return Response(byte_io.read(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={
            "Content-Disposition": f"attachment; filename=RICEF_{resume_name}.docx"
        })
    else:
        raise HTTPException(status_code=404, detail="Resume not found")


