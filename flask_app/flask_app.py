from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Connect to MongoDB
MONGO_URI = os.environ["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client.my_database
collection = db.my_collection

@app.route("/postdata", methods=["POST"])
def post_data():
    data = request.get_json()
    if isinstance(data, list):
        result = collection.insert_many(data)
        inserted_ids = [str(id) for id in result.inserted_ids]
        return jsonify({"_ids": inserted_ids}), 201
    else:
        result = collection.insert_one(data)
        return jsonify({"_id": str(result.inserted_id)}), 201

@app.route("/getdata", methods=["GET"])
def retrieve_data():
    cursor = collection.find()
    data = []
    for document in cursor:
        document["_id"] = str(document["_id"])
        data.append(document)
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
