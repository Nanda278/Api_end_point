from flask import Flask, request
from covidDetails.covidDetails import covidDetails
import requests

app = Flask(__name__)             # create an app instance

@app.route("/helloWorld")                   # at the end point /
def hello():                      # call method hello
    return "Hello World!.. this is new changes"

@app.route("/getCovidDetailsByPincode", methods=["GET"])
def getDetailsByPincode():
    cov = covidDetails()
    pincode = request.args.get('pincode')
    responseMsg = cov.getDetailsByPincode(pincode)
    return responseMsg

@app.route("/totalcasesbycountry", methods=["GET"])
def getTotalCasesByCountry():
    cov = covidDetails()
    country = request.args.get("country")
    type= request.args.get("type")

    responseMsg,_,_,_ = cov.getTotalCasesInfo(entity=country, type=type)
    #responseMsg+= cov.getMapUrl(country)
    return responseMsg

@app.route("/gettopcountrydetails", methods=['GET'])
def getTopCountriesList():
    cov = covidDetails()
    entity = request.args.get("entity")
    sortType = request.args.get("sortType")
    type= request.args.get("type")
    type = type.replace("_", " ")
    df = cov.getdfFromType(type)
    responseMsg = cov.getTopCountriesList(entity=entity,df=df,sortType=sortType,type=type)
    return responseMsg

@app.route("/sendMail", methods=['POST'])
def sendMailtoUser():
    cov = covidDetails()
    data = request.json
    response = cov.sendMail(data)
    return response




if __name__ == "__main__":        # on running python app.py
    app.run(port=8010)