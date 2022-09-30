import json

json_path = '/home/jzy/PaperLearning/MyUbuntu/RCenterNet/data/airplane/annotations/val.json'
json_labels = json.load(open(json_path,"r"))
print(json_labels["info"])
