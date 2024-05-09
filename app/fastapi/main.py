from fastapi import FastAPI, HTTPException, Depends
from starlette.requests import Request
import tensorflow as tf
import tensorflow_addons as tfa
from keras.preprocessing import image
from PIL import Image
import io
import numpy as np
from sqlalchemy import create_engine, text, Table, desc
from sqlalchemy.orm import sessionmaker, Session
from models.species import Base, Species
from fastapi.middleware.cors import CORSMiddleware
from models.user import User, UserHistory, Feedback
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import json
import base64
import boto3

app = FastAPI()

origins = [
    "http://localhost", 
    "http://localhost:8000", 
    "http://ec2-instance-public-ip",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


model_path = 'insert model path'
custom_objects = {'TriangularCyclicalLearningRate': tfa.optimizers.TriangularCyclicalLearningRate}

with tf.keras.utils.custom_object_scope(custom_objects):
    model = tf.keras.models.load_model(model_path)
print("Model has been loaded")

aws_access_key_id = 'insert access key'
aws_secret_access_key = 'insert secret access key'
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

db_engine = create_engine("mysql://username:password@endpoint:port/Schema") 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base.metadata.create_all(bind=db_engine, tables=[Species.metadata.tables[table] for table in Species.metadata.tables] + [User.__table__] + [UserHistory.__table__])
   
@app.post("/register")
async def register_user(username: str, password: str, email: str):
    db = SessionLocal()
    new_user = User(username=username, password=password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username, User.password == password).first()

    if user:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/predict_species")
async def predict_species(request: Request, data: dict):
    try:
        # Access the username and image data from the JSON data
        username = data.get('username')
        image_data_base64 = data.get('image_data')

        # Decode the image data
        image_data = base64.b64decode(image_data_base64)
        # Load and preprocess the image
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((240, 240))  # Adjust the size as needed
        img_array = np.expand_dims(np.array(img), axis=0)

        # Make predictions
        predictions = model.predict(img_array)

        # Post-process predictions
        top_n = 5  # Number of top predictions to consider
        top_n_indices = np.argsort(predictions)[0][-top_n:][::-1]
        top_n_confidences = predictions[0, top_n_indices]

        db = SessionLocal()
        try:
            # Store the image in S3
            s3_key = f"{username}/image_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
            s3.upload_fileobj(
                io.BytesIO(image_data),
                'bucketname',
                s3_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            s3_url = f"https://bucketname.s3.amazonaws.com/{s3_key}"

            # Construct user history objects for all predictions
            user_histories = []
            species_names = []
            local_names = []
            uses_list = []
            for idx, (predicted_class, confidence) in enumerate(zip(top_n_indices, top_n_confidences), 1):
                species = db.query(Species).filter(Species.Serial_No == predicted_class).first()
                species_name = species.Species_Name
                local_name = species.Common_name
                uses = species.Uses

                # Append the values to the lists
                species_names.append(species_name)
                local_names.append(local_name)
                uses_list.append(uses)

                history_object = {
                    'username': username,
                    'prediction_result': {
                        'predicted_class': int(predicted_class),
                        'confidence': float(confidence),
                        'species_name': species_name,
                        'local_name': local_name,
                        'uses': uses
                    }
                }
                user_id = None
                if username:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        user_id = user.user_id

                user_history = UserHistory(
                    username=username,
                    user_id = user_id,
                    image_data=s3_url,  
                    prediction_result=history_object['prediction_result']
                )
                user_histories.append(user_history)

            # Store all user history objects in the database
            db.add_all(user_histories)
            db.commit()

        except Exception as e:
            print(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error storing user history")

        finally:
            db.close()

        # Return predictions for all classes
        all_predictions = [
            {
                'predicted_class': int(predicted_class),
                'confidence': float(confidence),
                'species_name': species_name,
                'local_name': local_name,
                'uses': uses
            }
            for predicted_class, confidence, species_name, local_name, uses
            in zip(top_n_indices, top_n_confidences, species_names, local_names, uses_list)
        ]

        return all_predictions

    except Exception as e:
        # If an error occurs during processing, raise an HTTPException
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")



@app.post("/feedback")
async def submit_feedback(data: dict):
    db = SessionLocal()
    try:
        username = data.get('username')
        feedback_text = data.get('feedback')
        image_data_base64 = data.get('image_data')

        # Decode the image data
        image_data = base64.b64decode(image_data_base64)

        # Save the image to S3 in the 'feedback' folder
        s3_key = f"feedback/{username}/image_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
        s3.upload_fileobj(
                io.BytesIO(image_data),
                'bucketname',
                s3_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
        )        
        s3_url = f"https://bucketname.s3.amazonaws.com/{s3_key}"

        # Create a new feedback entry in the database
        feedback_entry = Feedback(username=username, image_path=s3_url, feedback=feedback_text)
        db.add(feedback_entry)
        db.commit()

        return {"message": "Feedback submitted successfully"}

    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")
    finally:
        db.close()

def get_feedback(db):
    return db.query(Feedback).all()

@app.get("/get_feedback")
async def get_feedback_endpoint():
    db = SessionLocal()
    try:
        feedback_entries = get_feedback(db)
        return {"feedback": feedback_entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback: {str(e)}")
    finally:
        db.close()

@app.get("/get_user_history/{username}")
async def get_user_history(username: str):
    try:
        # Create a new database session
        db = SessionLocal()

        # Query user history records for the specified username, ordered by created_at in descending order, and limit to 20 records
        user_histories = db.query(UserHistory).filter(UserHistory.username == username).order_by(desc(UserHistory.created_at)).limit(20).all()

        # Check if any user history records were found
        if not user_histories:
            raise HTTPException(status_code=404, detail="User history not found")

        # Convert user history objects to dictionaries for response
        history_records = []
        for history in user_histories:
            history_records.append({
                'id': history.id,
                'username': history.username,
                'user_id': history.user_id,
                'image_data': history.image_data,
                'created_at': history.created_at,
                'prediction_result': history.prediction_result
            })

        return {"history": history_records}

    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=f"Error retrieving user history: {str(e)}")
    finally:
        # Close the database session
        db.close()

