"""
Simple app to upload an image via a web form 
and view the inference results on the image in the browser.
"""

import argparse
import io
import os
import json
import glob
from PIL import Image
from uuid import uuid4
import torch
from flask import Flask, render_template, request, redirect,url_for
import numpy as np

def DeleteAllFiles(filePath):
    if os.path.exists(filePath):
        for file in os.scandir(filePath):
            os.remove(file.path)
            
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        DeleteAllFiles('C:\\web\\yolov5-flask\\static\\aft')  #파일삭제
        DeleteAllFiles('C:\\web\\yolov5-flask\\static\\bef')
        
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files.getlist("file")
        if not file:
            return

        pf=[]
        for file in file:
            filename = file.filename.rsplit("/")[0]
            print("진행 중 파일 :", filename)

            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))
            # print(img)
            img.save(f"static/bef/{filename}", format="JPEG")
            print('원본 저장')

            results = model(img, size=640)
            results.render()  # updates results.imgs with boxes and labels
            data = results.pandas().xyxy[0][['name']].values.tolist()
            print("데이터:",data)

            for img in results.imgs:
                img_base64 = Image.fromarray(img)
                img_base64.save(f"static/aft/{filename}", format="JPEG")
                print('디텍트 저장')

            if len(data) == 0:
                pf.append("PASS")
            if len(data) != 0:
                pf.append("FAIL")
            print(pf)
            root = "static/aft"
            if not os.path.isdir(root):
                return "Error : not found!"
            files = []
            for file in glob.glob("{}/*.*".format(root)):
                fname = file.split(os.sep)[-1]
                files.append(fname)
            print("파일스 :",files)
            firstimage = "static/aft/"+files[0]
            print("파일1 :",firstimage)
        return render_template("imageshow.html",files=files,pf=pf,firstimage=firstimage,enumerate=enumerate,len=len)
    return render_template("index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask app exposing yolov5 models")
    parser.add_argument("--port", default=5000, type=int, help="port number")
    args = parser.parse_args()

    model = torch.hub.load(
        'ultralytics/yolov5', 'custom', path='C:\web\yolov5-flask\yolov5l.pt', autoshape=True
    )  # force_reload = recache latest code
    model.eval()

    flask_options = dict(
        host='0.0.0.0',
        debug=True,
        port=args.port,
        threaded=True,
    )

    app.run(**flask_options)

