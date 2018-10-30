from flask import Flask,Response,request
import os, uuid, sys
from flask_cors import CORS
from flask import send_file
import json
from azure.storage.blob import BlockBlobService, PublicAccess
import pandas


app = Flask(__name__)
download_loc = os.path.dirname(os.path.abspath(__file__))+"\\"
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/Image')
def get_image():
    try:
        # Add '_DOWNLOADED' as prefix to '.txt' so you can see both files in Documents.
        full_path_to_file2 = os.path.join(download_loc,
                                          request.args.get('filename'))
        return send_file(full_path_to_file2, mimetype='image/jpg')

    except Exception as e:
        print(e)


@app.route('/Images')
def get_all_image():
    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name='team14dvnhack',
                                              account_key='KRW8lraTG0k7a0GGTKORvvjUHPn4Tp06zx+KGizw/JxlhCmcm6xrYwZXiValDHYKiPEGvR4u73DPWSfiVAUfPQ==')

        list_of_images = []
        container_name = 'team14dvnhackblob'
        local_folder = download_loc
        generator = block_blob_service.list_blobs(container_name)
        for blob in generator:
            full_path_to_file2 = os.path.join(local_folder , blob.name)
            if ".JPG" in blob.name or ".jpg" in blob.name:
                one_image = {}
                one_image["Name"] = blob.name
                one_image["ModifiedTime"] = str(blob.properties.last_modified)
                list_of_images.append(one_image)
            block_blob_service.get_blob_to_path(container_name, blob.name, full_path_to_file2)

        for each_value in list_of_images:
            if each_value["Name"].split(".JPG")[0]:
                prediction_data = pandas.read_csv(local_folder + each_value["Name"].split(".JPG")[0]+".csv")
                each_value["Reason"] = prediction_data["Reason"][0]
                each_value["Severity"] = get_severity((prediction_data["Inner CS"][0]+prediction_data["Outer CS"][0])/2)

        data = {
            'output': list_of_images
        }
        json_output = json.dumps(data)
        return Response(json_output, status=200, mimetype='application/json')

    except Exception as e:
        print(e)


@app.route('/Drillbit')
def get_drill_details():
    try:
        file_name = request.args.get('filename')
        compressor_data = {}
        file_name_concat = ''.join([download_loc, file_name, ".csv"])
        print("Nageeeeeeeeeee "+file_name_concat)
        prediction_data = pandas.read_csv(file_name_concat)
        compressor_data["InnerCS"] = str(prediction_data["Inner CS"][0])
        compressor_data["OuterCS"] = str(prediction_data["Outer CS"][0])
        compressor_data["DullCode"] = str(prediction_data["Dull Code"][0])
        compressor_data["Area"] = str(prediction_data["Area"][0])
        compressor_data["Seals"] = str(prediction_data["Seals"][0])
        compressor_data["Gauge"] = str(prediction_data["Gauge"][0])
        compressor_data["ODC"] = str(prediction_data["ODC"][0])
        compressor_data["Reason"] = str(prediction_data["Reason"][0])

        data = {
            'output': compressor_data
        }
        json_output = json.dumps(data)
        return Response(json_output, status=200, mimetype='application/json')

    except Exception as e:
        print(e)


def get_severity(value):
    if value < 3:
        return "success"
    if 7 > value > 3 :
        return "warning"
    else:
        return "danger"


if __name__ == '__main__':
    app.run()
