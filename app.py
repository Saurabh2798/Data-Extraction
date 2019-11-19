# imports
import os
import re
import sys
import cv2
import base64
import numpy as np
from PIL import ImageFile
from PIL import Image
from flask import Flask, request, jsonify
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/app/vendor/tesseract-ocr/bin/tesseract'
ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    resp = jsonify({
        u'status': 404,
        u'message': u'Resource not found'
    })
    resp.status_code = 404
    return resp


@app.route('/')
def api_root():
    resp = jsonify({
        u'status': 200,
        u'message': u"Please visit /extract_date to view working"
    })
    resp.status_code = 200
    return resp


@app.route("/extract_date", methods=['POST'])
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
    # image = Image.open(base64.b64decode(bs64_string))
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

    # regex7 = days + months + separators + years # matches date types 09Jul-19
    # regex8 = months + days + separators + years # matches date types Jun19'19

    # + regex7 + "|" + regex8+
    regexToMatch = "(" + regex1 + "|" + regex2 + "|" + regex3 + \
        "|" + regex4 + "|" + regex5 + "|" + regex6 + "|" + ")"

    match = re.findall(regexToMatch, text)
    for tup in set(match):
        for elem in tup:
            if(len(elem) > 6):
                return jsonify({'date': str(elem)})

    return jsonify({'date': str('null')})


if __name__ == '__main__':
    app.run()
