# imports
from datetime import datetime
import dateutil.parser
import os
import re
import sys
import cv2
import base64
import numpy as np
from PIL import ImageFile
from PIL import Image
from flask import Flask, request, jsonify, render_template
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
ImageFile.LOAD_TRUNCATED_IMAGES = True

# create flask app
app = Flask(__name__)

# error handler
@app.errorhandler(404)
def not_found(error):
    resp = jsonify({
        u'status': 404,
        u'message': u'Resource not found'
    })
    resp.status_code = 404
    return resp

# root
@app.route('/')
def api_root():
    resp = jsonify({
        u'status': 200,
        u'message': u"Please visit /extract_date to view working"
    })
    resp.status_code = 200
    return resp

# /extract_date
@app.route("/extract_date", methods=['GET', 'POST'])
def extract_date_from_img():
    """
    This funciton takes in an image, and extracts date from it

    Arguments:
        img -- The input image for which date needs to be extracted

    Returns:
        date -- returns date in YYYY-MM-DD format
    """

    # get raw data
    data = request.get_json()
    bs64_string = data["base_64_image_content"]

    # Decode base64 image and read it
    nparr = np.fromstring(base64.b64decode(bs64_string), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Use pytesseract to extract text from image
    text = pytesseract.image_to_string(image, lang="eng")

    # use regex to find various date patterns
    monthsShort = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    monthsLong = "January|February|March|April|May|June|July|August|September|October|November|December"
    monthSingleDigit = "\d{1}"
    months = "(" + monthsShort + "|" + monthsLong + \
        "|" + monthSingleDigit + "|" + ")"
    separators = "[,'/-]"
    days = "\d{2}"
    years = "(" + "\d{4}" + "|" + "\d{2}" + "|" + ")"

    regex1 = months + separators + days + separators + years

    # to match dd <sep> mm <sep> yyyy / mm <sep> dd <sep> yyyy
    regex2 = days + separators + months + separators + years

    regex3 = days + separators + days + separators + years

    # to match dd <sep> mm <sep> yy
    regex4 = days + separators + days + separators + days

    # to match m <sep> dd <sep> yyyy
    regex5 = months + separators + days + separators + years
    regex6 = years + separators + days + separators + days

    # match any of the above regexes
    regexToMatch = "(" + regex1 + "|" + regex2 + "|" + regex3 + \
        "|" + regex4 + "|" + regex5 + "|" + regex6 + "|" + ")"

    # find above regex patterns
    match = re.findall(regexToMatch, text)

    # iterate over the tuples and extract proper dates, exclude remaining
    for tup in set(match):
        for elem in tup:
            if(len(elem) > 6):
                formatted_date = format_date(elem)
                return jsonify({'date': str(formatted_date)})
    return jsonify({'date': str('null')})


def format_date(date):
    """
    This function converts date to the required output format

    Arguments:
        date -- date as detected by OCR + regex

    Returns:
        unified date in YYYY-MM-DD format
    """

    oldformat = dateutil.parser.parse(date)
    datetimeobject = datetime.strptime(str(oldformat), '%Y-%m-%d  %H:%M:%S')
    newformat = datetimeobject.strftime('%Y-%m-%d')
    return newformat


if __name__ == '__main__':
    app.run()
