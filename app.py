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

# path to tesseract on heroku
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
        u'message': u"Please send a POST request to /extract_date to view working"
    })
    resp.status_code = 200
    return resp

# /extract_date
@app.route("/extract_date", methods=['GET', 'POST'])
def extract_date_from_img():
    """
    This function takes in an image, and extracts date from it

    Arguments:
        img -- The input image for which date needs to be extracted

    Returns:
        date -- returns date in YYYY-MM-DD, null is not identified format
    """

    # get raw data
    data = request.get_json()
    bs64_string = data["base_64_image_content"]

    # Decode base64 image and read it
    nparr = np.fromstring(base64.b64decode(bs64_string), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # some preprocessing before passing it through tesseract
    # upscale the image
    resized_image = cv2.resize(image, (1191, 2000))

    # unsharp mask
    gaussian_3 = cv2.GaussianBlur(resized_image, (9, 9), 10.0)
    unsharp_image = cv2.addWeighted(
        resized_image, 1.3, gaussian_3, -0.7, 0, image)

    # Use pytesseract to extract text from the processed image
    text = pytesseract.image_to_string(unsharp_image, lang="eng")

    # use regex to find various date patterns
    regex7 = "\w{3}\s\d+,\s\d+"  # for dates like Sep 29, 2019
    regex8 = "\d+\-\d+\-\d+"  # 29-10-2018
    regex9 = "\d+\/\w{3}\/\d+"  # 29/May/1998
    regex10 = "\w{3}\s\d+\.\s\d+"  # May 29. 2019
    regex11 = "\w{3}\d+\'\d+"  # Jun19'19
    regex12 = "\d+\s\w+\'\d+"  # 20 Jun'19
    regex13 = "\w+\s\d+,\d+"  # JANUARY 30,2018
    regex14 = "\d+\/\d+\/\d+"  # 29/10/2018, 9/10/2018

    # match any of the above regexes
    regexToMatch = "|".join(
        [regex7, regex8, regex9, regex10, regex11, regex12, regex14, regex13])
    match = re.findall(regexToMatch, text)
    #print("match: ", match)

    # iterate over the matches and extract proper dates, exclude remaining
    for elem in match:

        # filter out date values which are not possible
        if(len(elem) > 6):
            format_date(elem)
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
    try:

        # parse the date received
        oldformat = dateutil.parser.parse(date)

        # strip time out of it
        datetimeobject = datetime.strptime(
            str(oldformat), '%Y-%m-%d  %H:%M:%S')
        newformat = oldformat.strftime('%Y-%m-%d')

        # return this date in YYYY-MM-DD format
        return newformat
    except ValueError:
        pass


if __name__ == '__main__':
    app.run()
