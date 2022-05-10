#!/usr/bin/env python3
from flask import Blueprint, render_template

v1_root = Blueprint('home', __name__)

@v1_root.route('/', methods=['GET'])
def landing_page():
    return render_template('home.html')
