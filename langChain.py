#!/usr/bin/env python
from fastapi import FastAPI, Request
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes
import os 
from pydantic import BaseModel
from fastapi.responses import FileResponse
from lat import resume_content
from dotenv import load_dotenv
load_dotenv()
print(type(resume_content))
import lat1


# Environment variable for API key
os.environ["TOGETHER_API_KEY"] = os.getenv('together_api')
user_bg = '''
Here is the professional background of the user:
**Professional Summary**

I began my coding journey at age 14, focusing on game development in Unity 3D using C#, and expanded my skills to include Blender for 3D modeling and HTML/CSS. During my Bachelor of Technology in Computer Science, I delved into C, C++, Python, and Java, mastering core computer science concepts such as data structures, algorithms, databases, compiler design, and computer architecture. My interest in neural networks and machine learning grew during this time, fueled by Andrew Ng’s courses and the 3blue1brown YouTube channel.

Upon graduating, I joined Accenture as a Fullstack Software Engineer. My role involved utilizing Java and frameworks like Spring MVC, Spring Boot, and Hibernate to develop functionalities, resolve defects, and perform unit testing in an Airplane Cargo Management project. I also developed and maintained interactive user interfaces with React, wrote SQL queries, managed microservices, and utilized GIT and JIRA for version control and project management.

Following this, I pursued a Master’s in Computer Science at the University of Texas at Arlington, where I excelled academically and worked as a Graduate Research and Teaching Assistant. My research included developing a VR video recommendation system using PyTorch and a graph-learning model, achieving over 68% improvement in recommendation precision. I co-authored a research paper accepted at the ACM MobiCom conference and used Docker to create isolated development environments. Additionally, I collected data from participants and developed adaptive bitrate streaming for VR, integrating human factors for improved video quality.

I am deeply passionate about machine learning and generative AI, continually updating my knowledge and skills. I have implemented various projects, including:

- **AI Agent for Diet Management:** Designed an AI chatbot using LangChain to interact with dietary data stored in PostgreSQL, incorporating custom SQL executions and providing a user-friendly interface with Express.js.
- **Automatic YouTube Shorts Generator:** Created an AI-driven system to generate YouTube Shorts using LLMs, diffusion models, and text-to-speech technologies from the Huggingface hub.
- **Breast Cancer Detection:** Developed a VGG11 vision model with PyTorch for classifying breast cancer into three categories, achieving notable validation accuracy.
- **VR Earth/Moon Explorer:** Built a VR application in Unity 3D to explore Earth and the Moon, utilizing REST APIs for geospatial data and converting it into 3D models.
- **Diffusion Model for Faces:** Trained a UNet2D diffusion model on the MetFaces dataset to generate artistic human faces.
- **Automatic Job Application System:** Employed LLMs and web scraping techniques to automate job applications, mapping fields and processing responses to fill application details.

I am committed to solving complex problems and continuously exploring innovative solutions through rigorous coding and in-depth understanding of advanced concepts.
'''

skills_template_content = '''

Given the user skills {skills}
rearrange the skills based on the Job description. Make it appealing to the recruiter.
output should be comma separated skills.
'''
projects_template_content = '''
Given the project {project_content}
Rewrite the project description such that it is more aligned with job description.
Make it very appealing to the recruiter.
output should a single paragraph less than 100 words.
'''


# 1. Create prompt template
system_template = '''
given the professional background of the user, {user_bg}
Provided the job description: {jd}  
'''

system_template = PromptTemplate(
    template=system_template,
    input_variables=["user_bg","jd"]  # Corrected input variables definition
)

skills_template = PromptTemplate(
    template=f"{system_template.template}\n\n{skills_template_content}",
    input_variables=["user_bg", "jd", "skills"]
)
projects_template= PromptTemplate(
     template=f"{system_template.template}\n\n{projects_template_content}",
     input_variables=["user_bg","jd","project_content"]
)

# 2. Create model
model = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=os.environ["TOGETHER_API_KEY"],
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
)

# 3. Create parser
parser = StrOutputParser()

# 4. Define chain
def process_project_chain(jd: str, project_content: str):
    # Fill the prompt with user-provided data
    prompt = projects_template.format(user_bg = user_bg, jd=jd,project_content=project_content)
    print(prompt)
    response = model.invoke(prompt)
    return parser.parse(response)

def process_skills_chain(jd:str,skills:str):
    prompt = skills_template.format(user_bg=user_bg,jd=jd,skills=skills)
    #print(prompt)
    response = model.invoke(prompt)
    return parser.parse(response)


# FastAPI model to handle input from the request body
class InputData(BaseModel):
    jd: str
    project_content: str

class ResumeContent(BaseModel):
    skills:str

class ResumeSkills(BaseModel):
     jd:str
     skills:str

class GenerateResumeInput(BaseModel):
    skills: str

# 5. App definition
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

# 6. Create a route that accepts POST requests with the JD and project content
@app.post("/process")
async def process_input(input_data: InputData):
    # Get data from the request body
    jd = input_data.jd
    project_content = input_data.project_content
    
    # Run the chain with user-provided JD and project content
    output = process_project_chain(jd, project_content)
    return {"output": output}

@app.post("/process_skills")
async def process_skills(input_data:ResumeSkills):
     jd = input_data.jd
     skills = input_data.skills
     print(jd,skills)
     output = process_skills_chain(jd,skills)
     lat1.resume_content["skills"] = [output]
     return {"output":output}

@app.post("/processed_resume_content")
async def processed_resume_content(input_data:ResumeContent):
        skills = input_data.skills
        print(skills)

@app.get("/")
async def UI():
    
    return FileResponse("/Users/venkateshwarreddy/Desktop/V/webdrivers/AI_WEB/AUTOMATIC_RESUME/templates/form.html") 

@app.get("/resume")
async def get_resume_content():
    # Return resume content dictionary
    return resume_content

@app.post("/generate_resume")
async def generate_resume(input_data: GenerateResumeInput):
    skills = input_data.skills
    lat1.resume_content["skills"] = [skills]
    lat1.main()
    return {"message": "Resume generated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
