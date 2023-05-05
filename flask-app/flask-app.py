from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Connect to MongoDB
MONGO_URI = os.environ["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client.my_database
collection = db.my_collection

@app.route("/postdata", methods=["POST"])
def top10():
    data = request.get_json()
    result = collection.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201

@app.route("/getdata/<id>", methods=["GET"])
def retrive(id):
    document = collection.find_one({"_id": ObjectId(id)})
    if document:
        document["_id"] = str(document["_id"])
        return jsonify(document), 200
    else:
        return "Not found", 404
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
