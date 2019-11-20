# Data-Extraction

The api is live at: https://date-extract-api.herokuapp.com/

To view working, please visit the testing section below.

## Approach used -
  - Used pytesseract to detect text from images
  - used regex for extracting all the possible date formats in the detected text
  - used Flask to serve the app
  - deployed to Heroku

## Results -

### Actual receipt image
![](actual-receipt.jpeg)

### Testing using Postman

#### 1. Local
![](results/results-postman.png)

#### 2. Heroku
![](results/results-heroku-1.png)
![](results/results-heroku-2.png)

