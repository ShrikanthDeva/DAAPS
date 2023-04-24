import os
from pymongo import MongoClient
import numpy as np
import cv2

sample = cv2.imread("C:\Users\shri1\sih\sih-project-2022\sih-project-final\fingerdata\374727291698.bmp")
client = MongoClient("mongodb+srv://shrikanth:aadhar_data@cluster0.6nbl1l4.mongodb.net/?retryWrites=true&w=majority")
db = client["aadharDB"]
finger_data = db["fingerDB"]
doc = {
    "finger": sample.tolist(),
    "Aadhar": "839314868452"
}
finger_data.insert_one(doc)
