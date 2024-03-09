import json

def requestToJson(request):
    raw_data = request.data
    data_str = raw_data.decode('utf-8')
    return json.loads(data_str)