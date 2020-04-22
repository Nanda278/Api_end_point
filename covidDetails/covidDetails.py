from geopy.geocoders import Bing
import requests
import pandas as pd
import re
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
from requests.utils import requote_uri


class covidDetails:

    def __init__(self):
        self.jhconfirmedcases = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        self.jhrecoveredcases = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
        self.jhdeathcases = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
        #sam =sample()

    def getDetailsByPincode(self, entity):
        geolocator = Bing(api_key="Ar-aTc8AF9MnqnsJAbSHorGLYZUugT5Rd2gmD6Aq6Cd-z-kMzJ71u3Ku7h_s0MNh")
        zipcode =str(entity)
        location = geolocator.geocode(zipcode, include_country_code=True, include_neighborhood=True)
        resonseMSg = ""
        try :
            countryValues = location.raw
            country = "IN" if(re.fullmatch(r'\d{6}',zipcode)) else countryValues['address']['countryRegionIso2']
            print("Country is ", country)

            try:
                if (country == "IN"):
                    response = requests.get("https://api.postalpincode.in/pincode/" + zipcode)
                    if (response.status_code == 200):
                        data = response.json()
                        correctStateName = data[0]['PostOffice'][0]['State']
                        correctStateName = "Puducherry" if(str(correctStateName).lower()=="pondicherry") else correctStateName
                        correctStateName = "Telengana" if (str(correctStateName).lower() == "telangana") else correctStateName
                        print(correctStateName)
                    else:
                        correctStateName = country
                resonseMSg, _, _, _ = self.getTotalCasesInfo(correctStateName,"All")
                #resonseMSg +=self.getMapUrl(country)


                return resonseMSg
            except Exception as ex:
                print(ex)
                resonseMSg1, _, _, _ = self.getTotalCasesInfo(country, "All")
                resonseMSg = "Sorry..!! I could not find the details for "+ zipcode.upper() +" \n Instead I am giving the below details " \
                               " as the "+zipcode.upper()+" belongs to "+country+"\n \n" \
                              ""+ resonseMSg1
                resonseMSg += self.getMapUrl(country, zoom=4)
                return resonseMSg

        except Exception as e:
            print(e)
            return "Sorry I am not able to recognize the zipcode "+ zipcode

    def getTotalCasesInfo(self, entity=None, type="All"):

        entity = "Telengana" if (str(entity).lower() == "telangana") else entity
        ccases = 0
        rcases = 0
        dcases = 0
        indiaFlag = True
        entity = str(entity).lower()
        try:
            if ((entity == 'none') | (entity == "") | (entity == 'globe') | (entity == "world") |
                    (entity == "All")):
                url = "https://corona.lmao.ninja/v2/all"
                entity = "World"

            else:
                url1 = "https://api.rootnet.in/covid19-in/stats/latest"
                responseValue = requests.get(url1)
                ind_data = responseValue.json()
                regionalData = ind_data['data']['regional']
                statesList = []
                data = {}
                for x in regionalData:
                    states = str(x['loc']).lower()
                    statesList.append(states)
                entity = str(entity).lower()
                try:
                    #indexMatch = statesList.index(entity)
                    #indexMatch = any(ele in entity for ele in statesList)
                    indexMatch = [key for key, val in enumerate(statesList)
                           if val.find(entity) != -1]
                    if (len(indexMatch)>0):

                        entity = statesList[indexMatch[0]]
                        entity = "**" + entity + "**"
                        data['cases'] = regionalData[indexMatch[0]]['confirmedCasesIndian']
                        data['recovered'] = regionalData[indexMatch[0]]['discharged']
                        data['deaths'] = regionalData[indexMatch[0]]['deaths']
                        data['active'] = 0
                        # data['countryInfo']['flag'] = "https://raw.githubusercontent.com/NovelCOVID/API/master/assets/flags/in.png"
                        responeMsg, ccases, rcases, dcases = self.formCasesString(data, type, entity)
                        responeMsg+= self.getMapUrl(entity)
                        indiaFlag = False
                    else:
                        url = "https://corona.lmao.ninja/v2/countries/" + entity
                except Exception as ex:
                    # geolocator = Bing(api_key="Ar-aTc8AF9MnqnsJAbSHorGLYZUugT5Rd2gmD6Aq6Cd-z-kMzJ71u3Ku7h_s0MNh")
                    # zipcode = str(entity)
                    # location = geolocator.geocode(zipcode, include_country_code=True, include_neighborhood=True)
                    try:
                        entity = str(entity) #location.raw['address']['countryRegionIso2']
                        url = "https://corona.lmao.ninja/v2/countries/" + entity
                    except Exception as exp:
                        print(exp)
                    print(ex)

            if (indiaFlag):
                print("URL for cases..", str(url))
                response = requests.get(url)
                if (response.status_code == 200):
                    data = response.json()
                    entity = entity if (entity == "World") else data['country']
                    entity = str(entity).title()
                    entity = "**" + entity + "**"
                    if (type == "All"):
                        ccases = data['cases']
                        rcases = data['recovered']
                        dcases = data['deaths']
                        accases = data['active']
                        responeMsg = "Hey, the latest covid-19 cases of " + f"{entity}" + " with \n \n" + "Confirmed cases as " + f"{ccases}" + "\n \n" \
                                                                                                                                                "and the Recovered Cases counts to " + f"{rcases}" + "\n \n" + "and finally the Death Cases are " + f"{dcases}"
                    elif (type == "confirmed"):
                        ccases = data['cases']
                        responeMsg = "The total confirmed covid-19 cases of " + f"{entity}" + " is " + f"{ccases}"
                    elif (type == "deaths"):
                        dcases = data['deaths']
                        responeMsg = "The total death cases of covid-19 in " + f"{entity}" + " is " + f"{dcases}"
                    elif (type == "recovered"):
                        rcases = data['recovered']
                        responeMsg = "The recovered cases for covid-19 in " + f"{entity}" + " " + f"{rcases}"
                    if ('countryInfo' in data):
                        responeMsg += "$$$" + data['countryInfo']['flag']
                    responeMsg += self.getMapUrl(entity,zoom=4)

                else:
                    responeMsg = self.getTotalCasesFromJPH(entity, type)
                    responeMsg += self.getMapUrl(entity,zoom=4)
                    #responeMsg = "Sorry!! I could not reach the api.."
        except Exception as ex:
            print(ex)
            responeMsg = "Sorry!! I could not recognized you.."
        return responeMsg, ccases,rcases,dcases

    def formCasesString(self, data, type, entity):
        ccases = 0
        rcases = 0
        dcases = 0
        responeMsg=""
        if (type == "All"):
            ccases = data['cases']
            rcases = data['recovered']
            dcases = data['deaths']
            accases = data['active']
            responeMsg = "Hey, the latest covid-19 cases of " + f"{entity}" + " with \n \n" + "Confirmed cases as " + f"{ccases}" + "\n \n" \
                           "and the Recovered Cases counts to " + f"{rcases}" + "\n \n" + "and finally the Death Cases are " + f"{dcases}"
        elif (type == "confirmed"):
            ccases = data['cases']
            responeMsg = "The total confirmed covid-19 cases of " + f"{entity}" + " is " + f"{ccases}"
        elif (type == "deaths"):
            dcases = data['deaths']
            responeMsg = "The total death cases of covid-19 in " + f"{entity}" + " is " + f"{dcases}"
        elif (type == "recovered"):
            rcases = data['recovered']
            responeMsg = "The recovered cases from covid-19 in " + f"{entity}" + " is " + f"{rcases}"

        #responeMsg += "$$$" + data['countryInfo']['flag']


        return  responeMsg, ccases,rcases,dcases

    def getTopCountriesList(self,entity=1, df=None, sortType="DESC", type="cases"):
        try:
            if (entity == "" or entity == None):
                entity = 1
            groupedDF = df.groupby("Country/Region")[df.columns[-1]].sum()
            groupedDF = groupedDF.reset_index()
            groupedDF.columns = ['country', 'total']
            if (sortType == "DESC"):
                groupedDF = groupedDF.sort_values(['total'], ascending=False)
            else:
                groupedDF = groupedDF.sort_values(['total'], ascending=True)

            results = groupedDF.head(int(entity)).values
            if (len(results) > 0):
                type = str(type).title()
                responseMsg = "Top Countreis with " + f"{type} " + " \n \n"
                for xx in results:
                    # print(i)

                    responseMsg += "***" + str(xx[0]).title() + "*** has \t  " + f"{xx[1]}  cases \n \n"

            else:
                responseMsg = "Hey sorry, I couldn't recognise your message. Please give an appropriate message. \n " \
                              "For Eg., country with most recovered cases.."
        except Exception as e:
            responseMsg = "Hey sorry, I couldn't recognise your message. Please give an appropriate message. \n " \
                          "For Eg., country with most recovered cases.."
            print(e)
        return responseMsg

    def getdfFromType(self, type):
        df =pd.DataFrame()
        if(type == "most confirmed cases" or type=="less confirmed cases"):
            df = pd.read_csv(self.jhconfirmedcases)
        elif(type=="most recovered cases" or type=="less recovered cases"):
            df= pd.read_csv(self.jhrecoveredcases)
        elif(type=="most death cases" or type=="less death cases"):
            df = pd.read_csv(self.jhdeathcases)
        return df

    def getTotalCasesFromJPH(self, entity, type="All"):
        responseMsg = ""
        if(type=="All" or type=="" or type==None):
            df_c = pd.read_csv(self.jhconfirmedcases)
            df_r = pd.read_csv(self.jhrecoveredcases)
            df_d = pd.read_csv(self.jhdeathcases)
            ccases = self.getResultFromDF(df_c, entity, "confirmed cases")
            rcases = self.getResultFromDF(df_r, entity, "recovered cases")
            dcases = self.getResultFromDF(df_d, entity, "death cases")
            responseMsg +="Hey..!! The latest status of covid-19 in **"+ str(entity).title()+"** \n \n"
            responseMsg += ccases+"\n \n"
            responseMsg += rcases + "\n \n"
            responseMsg += dcases + "\n \n"
        elif(type=="confirmed"):
            df_c = pd.read_csv(self.jhconfirmedcases)
            ccases = self.getResultFromDF(df_c, entity, "confirmed cases")
            responseMsg += "Hey..!! The latest status of covid-19 in **" + str(entity).title() + "** \n \n"
            responseMsg += ccases + "\n \n"
        elif(type=="recovered"):
            df_r = pd.read_csv(self.jhrecoveredcases)
            rcases = self.getResultFromDF(df_r, entity, "confirmed cases")
            responseMsg += "Hey..!! The latest status of covid-19 in **" + str(entity).title() + "** \n \n"
            responseMsg += rcases + "\n \n"
        elif(type=="deaths"):
            df_d = pd.read_csv(self.jhdeathcases)
            dcases = self.getResultFromDF(df_d, entity, "recovered cases")
            responseMsg += "Hey..!! The latest status of covid-19 in **" + str(entity).title() + "** \n \n"
            responseMsg += dcases + "\n \n"
        if "Hey Sorry" in responseMsg:
            responseMsg = "Hey Sorry..! I could not find any details for "+str(entity).title()

        return responseMsg

    def getResultFromDF(self, df, county, type="cases"):
        groupedDF = df.groupby("Country/Region")[df.columns[-1]].sum()
        groupedDF = groupedDF.reset_index()
        groupedDF.columns = ['country', 'total']
        groupedDF = groupedDF[groupedDF['country'].str.lower() == str(county).lower()]
        try:
            responseValue = groupedDF['total'].values[0]
            responseValueMsg = "the total number of " + f"{type}" + " in " + f"{county}" + " is " + f"{responseValue}"
        except Exception as e:
            print(e)
            responseValueMsg = "Hey Sorry, I could not find any cases for " + county

        return responseValueMsg

    def sendMail(self, data):
        print(data)
        data = json.loads(data)
        email = str(data['mailid'])
        mobile = str(data['mobile'])
        name = str(data['name'])
        if (str(email) == ""):
            responseMsg = "Please provide a valid email"
        else:
            try:
                #msg = MIMEMultipart()
                msg = EmailMessage()
                fromMy = 'covid19.luisbot@yahoo.com'  # fun-fact: from is a keyword in python, you can't use it as variable, did abyone check if this code even works?
                to = str(email).lower()
                subj = 'Covid-19 Details And Preventive Measures'

                from datetime import date
                today = date.today()
                # print("Today's date:", today)
                date = str(today)
                _, totalccases, totalrcases, totaldcases = self.getTotalCasesInfo(entity=None,type="All")
                message_text = "Hi " + name + " \n \n As on #date total number of covid-19 cases in the World is #totalccases, \n total number of recovered" \
                                                       "cases is #totalrcases and \n total number of death cases is #totaldcases. \n \n \n " \
                                                        "In the near feature we will be provide the details via SMS to your registed number " \
                                                        "#mobile \n \n" \
                                                       "Preventive Measures are  : \n \n" \
                                                       "1. STAY Home \n " \
                                                       "2. KEEP a safe distance \n " \
                                                       "3. WASH your hands often \n " \
                                                       "4. COVER your cough \n " \
                                                       "5. SICK ? Please call the helpline"

                message_text = message_text.replace("#date", date)
                message_text = message_text.replace("#mobile", mobile)
                message_text = message_text.replace("#totalccases", str(totalccases))
                message_text = message_text.replace("#totalrcases", str(totalrcases))
                message_text = message_text.replace("#totaldcases", str(totaldcases))
                #msg.attach(MIMEText(message_text,'plain'))
                msg.set_content(message_text)

                filename = "PreventiveMeasures.pdf"
                with open("PreventiveMeasures.pdf", 'rb') as fp:
                    pdf_data = fp.read()
                    ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    msg.add_attachment(pdf_data, maintype=maintype, subtype=subtype, filename=filename)


                msg['From'] = fromMy
                msg['To'] = to
                msg['Subject'] = subj
                #msg['Date'] = date
                #msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (fromMy, to, subj, date, message_text)

                #text = msg.as_string()
                text = msg
                username = str('covid19.luisbot@yahoo.com')
                password = str('wyox bkly chvz plpn')

                server = smtplib.SMTP("smtp.mail.yahoo.com", 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(username, password)
                server.send_message(text,fromMy, to)
                server.quit()
                return "Thank you..!! Details about covid-19 and the preventive measure is send to your email " + f"{email}"
            except Exception as ex:
                print(ex)
                responseMsg = "Thank you..!! Error in sending Email"

        return responseMsg

    def getMapUrl(self, entity, zoom=7):
        dynamicMapUrl = "https://www.mapquestapi.com/staticmap/v4/getmap?key=lYrP4vF3Uk5zgTiGGuEzQGwGIVDGuy24" \
                        "&size=600,600&type=map&imagetype=jpg&zoom=#zoom&scalebar=false&traffic=false" \
                        "&center=#center" \
                        "&xis=https://s.aolcdn.com/os/mapquest/yogi/icons/poi-active.png,1,c,40.015831,-105.27927&ellipse=fill:0x70ff0000|color:0xff0000|width:2|40.00,-105.25,40.04,-105.30"

        try:
            zoom =str(zoom)
            dynamicMapUrl = requote_uri(dynamicMapUrl)
            geolocator = Bing(api_key="Ar-aTc8AF9MnqnsJAbSHorGLYZUugT5Rd2gmD6Aq6Cd-z-kMzJ71u3Ku7h_s0MNh")
            location = geolocator.geocode(entity, include_country_code=True)
            lat = location.raw['point']['coordinates'][0]
            long = location.raw['point']['coordinates'][1]
            latValues = str(lat)+ "," + str(long)
            dynamicMapUrl = dynamicMapUrl.replace("#center", latValues)
            dynamicMapUrl = dynamicMapUrl.replace("#zoom", zoom)

            responseValue = "$$$"+dynamicMapUrl
            print(dynamicMapUrl)
            # response = requests.get(dynamicMapUrl)
            # if(response.status_code==200):
            #     responseValue = "$$$"+ response.text
            # else:
            #     responseValue= ""
        except Exception as ex:
            print(ex)
            responseValue = ""
        return responseValue

