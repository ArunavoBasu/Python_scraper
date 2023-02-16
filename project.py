from flask import Flask, render_template, request, jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename = "scraper.log", level = logging.INFO)

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("ProjectScrap_index.html")

@app.route("/review", methods = ['POST'])
def reviewpage():
    if (request.method=='POST'):
        try:
            searchString = request.form['content'].replace(" ","")

            #flipkart website url and the item we want to search
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            # uReq --> used to hit any url from python in the world
            uclient = uReq(flipkart_url)

            #page source (html datas) are stored in this variable
            flipkartpage = uclient.read()
            uclient.close()

            #bs --> beautification, "html.parser" --> as the flipkartpage is a HTML element
            flipkart_html = bs(flipkartpage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class" : "_1AtVbE col-12-12"})
            box = bigboxes[0]
            productlink = "https://www.flipkart.com" + box.div.div.div.a['href']
            productreq = requests.get(productlink)
            prod_html = bs(productreq.text, "html.parser")
            comment_box = prod_html.findAll("div", {"class": "_16PBlm"})
            reviews = []
            for i in comment_box:
                try:
                    name = i.div.div.findAll("div", {"class": ""})[0].div.text
                except:
                    logging,info("name")

                try:
                    rating = i.div.div.div.div.text
                except:
                    rating = "No rating is given"
                    logging.info(rating)

                try:
                    commentHead = i.div.div.div.p.text
                except:
                    commentHead = "No comment head"
                    logging.info(commentHead)

                try:
                    comtag = i.div.div.find_all('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                myDict = {"Product": searchString, "Name": name, "Rating": rating, "Comment Head": commentHead, "Comments": custComment}

                reviews.append(myDict)

            logging.info("final log is {}".format(reviews))
            return render_template("ProjectScrap_result.html", reviews=reviews[0:len((reviews)-1)])
        except Exception as e:
            logging.info(e)
            raise e
            return "Something went wrong"  
    else:
        return render_template("ProjectScrap_index.html")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)
