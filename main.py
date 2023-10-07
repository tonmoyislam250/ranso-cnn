# import all the required libraries
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
import tempfile
import itertools
import pefile
import os, math
from queue import Queue
from threading import Thread
import argparse
from PIL import Image

from keras.utils.image_utils import img_to_array
from keras.applications import imagenet_utils

from fastapi import FastAPI, File, UploadFile
from starlette.responses import RedirectResponse

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scripts import exe_to_png
from scripts import peDataDumpPreprocess
from scripts import preprocessPNG

# creating fastApi app
app_desc = """<h2> Try uploading a Portable Executable(PE) file"""
app = FastAPI(description=app_desc)


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


@app.post("/predict")
def parse(file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1]
    _, path = tempfile.mkstemp(prefix="parser_", suffix=extension)

    with open(path, "ab") as f:
        for chunk in iter(lambda: file.file.read(10000), b""):
            f.write(chunk)

    # extract content
    content = pefile.PE(path, fast_load=True)
    img = None
    dataframe = peDataDumpPreprocess.createDataframeFromPEdump(content)
    binary_preds = peDataDumpPreprocess.getPredictions(dataframe)
    if binary_preds[1] * 100 > 60.0:
        img_path = exe_to_png.createGreyScaleImage(path)
        img = preprocessPNG.cnn_predict(img_path)
        return {
            "response": "OK",
            "path": path,
            "predictions": binary_preds[1],
            "malware": img,
        }
    else:
        return {
            "Response": "Your file is safe from malware.",
            "Malicious percentage": binary_preds[1] * 100,
        }
    # remove temp file
    os.close(_)
    os.remove(path)
