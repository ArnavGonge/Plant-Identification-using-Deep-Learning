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
   - The model can be found on the following link: https://drive.google.com/drive/folders/1D-qd0ZyJz0pcruI4deFHL7RDYKZ4X064?usp=sharing    

3. Install dependencies:
    - cd app/fastapi
    - pip install -r requirements.txt (it is recommended to create a venv using python-3.10 before)

4. Update path of the model:
   - Open main.py
   - Update model path on line 37

5. Enter credentials:
   - Enter AWS access key and secret access key on line 44 and 45.
   - Enter RDS credentials on line 48.
   - Create an S3 bucket and replace 'bucketname' on line 100, 104, 193, 197.

6. Run the FastAPI server:
   - uvicorn main:app --reload
  
7. Test the server:
   - Open http://localhost:8000/docs in your browser to check the API documentation and test them.
     
  
## Usage

The detailed information for each endpoint is given below:

1. /register:
   - Registers a new user.
   - Accepts user registration information (username, password and email) via HTTP POST request and stores it in the database.
   - Returns a success message upon successful registration.
     
2. /login:
   - Authenticates a user for login.
   - Validates user credentials (username and password) against the database. If valid, returns a success message; otherwise, raises a 401 Unauthorized HTTP exception.
     
3. /predict_species:
   - Predicts the species of a plant based on the provided image data.
   - Accepts request dictionary containing username and image data in base64 format.
   - Decodes the image data and preprocesses it.
   - Makes predictions using a pre-trained model.
   - Stores the image in an S3 bucket and the prediction results in the database.
   - Returns the top N predictions along with their confidence scores.
   - Returns a list of dictionaries containing the predicted class, confidence score, species name, local name, and uses for each predicted species.
   - Raises a 500 Internal Server Error HTTP exception if an error occurs during image processing or database storage.

4. /feedback:
   - Allows users to submit feedback along with an optional image.
   - Accepts request dictionary containing username, feedback text, and optional image data in base64 format.
   - Decodes the image data (if provided) and saves it to an S3 bucket.
   - Stores the feedback entry in the database.
   - Returns a message indicating whether the feedback was submitted successfully.
   - Raises a 500 Internal Server Error HTTP exception if an error occurs during image processing or database storage.

5. /get_feedback:
   - Retrieves all feedback entries from the database.
   - Raises a 500 Internal Server Error HTTP exception if an error occurs during database retrieval.
  
6. /get_user_history/{username}:
   - Retrieves user history records for a specified username.
   - Returns a JSON object with the key "history" containing a list of user history records.
   - Each history record includes:
       - id: Unique identifier of the history record.
       - username: Username of the user.
       - user_id: ID of the user.
       - image_data: URL or data representing the image.
       - created_at: Timestamp indicating when the history record was created.
       - prediction_result: Details of the prediction result associated with the history record.

    
## Model

1. Datasets: PlantCLEF 2015 dataset (https://lab.plantnet.org/LifeCLEF/PlantCLEF2015/) and an additional Indian Medicinal Plant Species dataset (https://www.kaggle.com/datasets/warcoder/indian-medicinal-plant-image-dataset) were used.
2. 553 species from the PlantCLEF dataset and 35 species from the Indian Medicinal Plant Species dataset were used; the species can be found in class_indices.csv
3. Only leaf and leaf-scan images are used from the PlantCLEF dataset.
4. Transfer learning from ImageNet weights on the EfficientNetV2S model was applied.
5. The loss function used was Keras categorical focal cross entropy.
6. Cyclic learning rate scheduler was used but can be replaced by a simple reduce learning rate on plateau function.
7. By process of transfer learning, first only the softmax layer was trained and then we gradually unfroze the remaining layers whilst keeping the batch normalization layers frozen.
   

## Docker image recreation

1. To recreate the docker image, just make sure the model is copied into the Dockerfile's working directory.
2. Update the model_path in main.py to what it would be inside the docker container (/app/<model_directory>).
3. Run the following commands from the Dockerfile directory.
    - docker build -t <image_name:tag> .
    - docker run -d -p <port>:8000 <image_name:tag>
      
   
## Android Application

The corresponding android application that works with this backend can be found in the following repository:
