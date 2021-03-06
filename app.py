from __future__ import print_function

from flask import Flask, request
from flask_restplus import Api, Resource
from flask_cors import CORS
from flask_mail import Mail, Message
import pandas as pd 
import numpy as np
import sys, os, time, json

from engine import ReconcileEngine
from grouping import FindGroupSum
from functions import csv_to_df, remaining_to_values
from config import mail_settings

flask_app = Flask(__name__)
flask_app.config.update(mail_settings)
mail = Mail(flask_app)
CORS(flask_app)

app = Api(app = flask_app, 
		  version = "1.0.2", 
		  title = "Reconcile APIs", 
		  description = "Find matching items statement.")

matching = app.namespace('main', description='Find matching')

@matching.route("/")
class MainClass(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error' })
	
	def post(self):
		try:
			# get files from client 
			file_book = request.form['file_book']
			file_bank = request.form['file_bank']
			date_range = request.form['date_range']

			# parse string (csv) to dataframe
			file_bookDf = csv_to_df(file_book)
			file_bankDf = csv_to_df(file_bank)

			print(file_book)
			print(file_bank)

			result_fields = ReconcileEngine(file_bookDf, file_bankDf, 0, int(date_range))
			associated = result_fields.bankDF.associate

			remainingLedger, remainingBank = remaining_to_values(file_bookDf, file_bankDf, associated)

			result_group = FindGroupSum(remainingBank, remainingLedger)
			resultGroup = pd.DataFrame(result_group.resultGroup).to_json(orient="index")
			unmatchedLedger = result_group.unableLedger
			unmatchedBank = result_group.unableBank

			print(associated)
			# check

			IndexToRemove = []
			for obj in result_group.resultGroup:
				IndexToRemove += obj['bank']
				for index in obj['ledger']:
					# get key of index in Series
					try:
						IndexToRemove.append(associated[associated == index].index[0])
					except:
						pass
					
			print(IndexToRemove)
			print(associated.drop(labels=IndexToRemove, inplace=True))

			# associated.drop(labels=IndexToRemove, inplace=True)
			associated.dropna(inplace=True)

			print(associated)

			resultJson = associated.to_json(orient="index")

			# print(json.dumps(json.loads(resultJson), indent=4, sort_keys=True))

			return [resultJson, resultGroup, unmatchedLedger, unmatchedBank]

		except KeyError as e:
			matching.abort(500, e.__doc__, status = "Could not perform reconciliation", statusCode = "500")

		except Exception as e:
			matching.abort(400, e.__doc__, status = "Incorrect or corrupted", statusCode = "400")


contact = app.namespace('contact')

@contact.route("/")
class MainClass(Resource):

	@app.doc(responses={ 200: 'OK', 400: 'Bad Request', 500: 'Internal Server Error' })
	
	def post(self):
		try:
			contact_form = request.form['contact']
			contact_form = json.loads(contact_form)
			
			email = contact_form["email"]
			name = contact_form["name"]
			category = contact_form["category"]
			comment = contact_form["comment"]

			msg = Message("User Contact - " + category,
                  sender=email,
                  recipients=["to@example.com"])
			msg.body = comment
			mail.send(msg)

			return 200

		except KeyError as e:
			matching.abort(500, e.__doc__, status = "Could not perform reconciliation", statusCode = "500")

		except Exception as e:
			matching.abort(400, e.__doc__, status = "Incorrect or corrupted", statusCode = "400")

if __name__ == '__main__':
    flask_app.run(debug=True, port=5000)