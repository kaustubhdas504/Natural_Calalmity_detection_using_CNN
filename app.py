
# -*- coding: utf-8 -*-

from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import tensorflow as tf
import h5py
import csv
from locale import locale_alias
##############################




#############################
# from tensorflow.compat.v1 import ConfigProto
# #from tensorflow.compat.v1 import InteractiveSession

# config = ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.2
# config.gpu_options.allow_growth = True
# session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input, ResNet50
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

import json

# Flask utils
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask import Flask, redirect, url_for, flash, request, render_template, session
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer





##########################################################
from flask import Flask, render_template, request,session,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
from keras.models import load_model
import pandas as pd
import numpy as np


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__,template_folder='template')

app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Register(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	name=db.Column(db.String(50),nullable=False)
	email=db.Column(db.String(50),nullable=False)
	password=db.Column(db.String(50),nullable=False)
	password2=db.Column(db.String(50),nullable=False)



class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Name=db.Column(db.String(50),nullable=False)
    Email=db.Column(db.String(50),nullable=False)
    Subject =db.Column(db.String(50),nullable=False)
    Message=db.Column(db.String(50),nullable=False)  

class Btc_usd(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Date=db.Column(db.String(50),nullable=False)
    Open=db.Column(db.String(50),nullable=False)
    High=db.Column(db.String(50),nullable=False)
    Low=db.Column(db.String(50),nullable=False)  
    Close=db.Column(db.String(50),nullable=False) 
    AdjClose=db.Column(db.String(50),nullable=False) 
    Volume=db.Column(db.String(50),nullable=False)   

# Model saved with Keras model.save()
MODEL_PATH ='best_model.h5'

# # Load your trained model
model = load_model(MODEL_PATH)
# model._make_predict_function()

def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(180, 180))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   
# x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="""Cyclone Safety Measures : 1. Leave early before your way to high ground or shelter gets flooded. 
        2. Do not delay and run the risk of being marooned. 
        3. If your house is securely built on high ground take shelter in the safe part of the house. However, if asked to evacuate do not hesitate to leave the place. 
        4. Board up glass windows or put storm shutters in place.  
        5. Provide strong suitable support for outside doors. """ 
    elif preds==1:
        preds="EarthQuake Safety Measures : 1. Protect yourself from falling objects. \n 2. Stop as quickly as safety permits and stay in the vehicle. \n Avoid stopping near or under buildings,overpasses, and utility wires.\n Stay away from outer walls, windows, fireplaces, and hanging objects \n If you are outside, go to an open area away from trees, telephone poles, and buildings."
    elif preds==2:
        preds="Flood  Safety Measures :1. Knowing your community’s evacuation route and warning signals, and identifying areas prone to flooding or landslides. \n 2. Chlorinating or boiling all water for drinking and food preparation Ensuring uninterrupted provision of safe drinking water is the most important preventive measure to be implemented following flooding, in order to reduce the risk of outbreaks of water-borne diseases. \n 3. Promoting good hygienic practices and safe food preparation techniques Do not use flood water to wash dishes, brush teeth or wash and prepare food. Always wash your hands with soap and water if you have been in contact with floodwater. \n 4. Avoiding walking or driving through flooded areas and standing water. Even the smallest amount of water can bring about significant dangers. You do not know if electrical lines have fallen in the water or hazardous chemicals exist. Cars and people can easily be swept away during a flood.  "
    elif preds==3:
        preds="Wild Fire  Safety Measures :  1. Clear combustible materials such as dried leaves and pine needles. \n 2. Cut down any tree limbs that are 15 feet or closer to the ground. This will help prevent the fire from spreading into your property’s tree line. \n 3. Remove any vines or vegetation that is on the side of your house or business. \n 4. Place any flammable lawn furniture in storage when not in use. \n 5. Opt for non-flammable decor, such as gravel as opposed to wood chips."
    return preds

@app.route("/")
def Home():
    return render_template('index.html',params=params)

@app.route("/register",methods=['GET','POST'])
def register():
	if(request.method=='POST'):
		name=request.form.get('name')
		email=request.form.get('email')
		password=request.form.get('password')
		password2=request.form.get('password2')
		error=""
		validate_email=Register.query.filter_by(email=email).first()
		if validate_email:
			error="email is already exists"
		else:
			if(password==password2):
				entry=Register(name=name,email=email,password=password,password2=password2)
				db.session.add(entry)
				db.session.commit()
			else:
				flash("plz enter right password")
		return render_template('register.html',params=params, error=error)
	return render_template('register.html',params=params)

@app.route("/login",methods=['GET' , 'POST'])
def login():
    if(request.method == 'GET'):
    	# import pdb;pdb.set_trace();
    	if('email' in session and session['email']):
    		return render_template('index1.html', params=params)
    	else:
    		return render_template('login.html', params=params)
    if(request.method == 'POST'):
    	email=request.form["email"]
    	password=request.form["password"]
    	login=Register.query.filter_by(email=email,password=password).first()
    	if login is not None:
    		session['email']=email
    		return render_template('index1.html',params=params)
    	else:
    		flash("plz enter right password")
    return render_template('login.html',params=params)



@app.route("/contact",methods=['GET','POST'])
def contact():
   
    if(request.method=='POST'):
        Name=request.form.get('Name')
        Email=request.form.get('Email')
        Subject =request.form.get('Subject')
        Message=request.form.get('Message')
        entry=Contact(Name=Name,Email=Email,Subject=Subject,Message=Message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)
   

@app.route('/')
def hello_world():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('Home')) 
    


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        result=preds
        return result
    
    
    return None

app.run(debug=True)