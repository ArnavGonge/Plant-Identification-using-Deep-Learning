# Plant Identification using Deep Learning

This project aims to develop a plant identification system using deep learning models. It includes a few backend APIs built with FastAPI to provide plant identification functionality based on uploaded images. The APIs link the backend to an AWS RDS instance.

## Features

- **Deep Learning Model**: Utilizes EfficientNetV2S deep learning model for plant species identification.
- **FastAPI Backend**: Provides a RESTful API for uploading images and receiving plant identification results, also has user registration, login and history storage.
- **Scalable Architecture**: Designed for scalability to handle a large number of user requests efficiently using Docker.
- **Documentation**: Includes comprehensive documentation for easy setup and usage.

## Installation

To run the plant identification backend locally, follow these steps:

1. Clone the repository:
   - git clone https://github.com/ArnavGonge/Plant-Identification-using-Deep-Learning
   - cd Plant-Identification-using-Deep-Learning
  
2. Download the model:
   - The model can be found on the following link:     

2. Install dependencies:
    - cd app/fastapi
    - pip install -r requirements.txt (it is recommended to create a venv using python-3.10 before)

3. Update path of the model:
   - Open main.py
   - Update model path on line 37

4. Run the FastAPI server:
   - uvicorn main:app --reload
  
5. Test the server:
   - Open http://localhost:8000/docs in your browser to check the API documentation and test them.
  
##Usage
     

