from cmath import nan
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
from fuzzywuzzy import fuzz

df = pd.read_csv("Template-GC_RDA_maDMP - GC DMP Overview.csv")
dict = json.load(open("GC_GCmaDMP_0.0.1.json"))

dictuuidlst = []
xluuidlst = []
matched = []
dictres = []
xlres = []

m_fieldname = []
m_title = []
m_desc = []

rd_title = []
rd_desc = []

rx_fieldname = []

##########################################
# UUID Residuals

for i in range(len(dict['packages'])):
    for e in dict['packages'][i]['events']:
        if e["entityUuid"] != nan:
            dictuuidlst.append(e["entityUuid"])

for u in df[' DSW knowledge model UUID']:
    if u != "n/a (top level)" and u != nan:
        xluuidlst.append(u)

for u in dictuuidlst:
    if u in xluuidlst:
        matched.append(u)
    else:
        dictres.append(u)

for u in xluuidlst:
    if u not in matched:
        xlres.append(u)

##########################################
# Association of UUIDs with question/desc/fieldnames

data = []
rowTemp = {
    'uuid': None,
    'fieldname': None,
    'title': None,
    'description': None,
    'type': None,
    'ratio_t': 0,
    'ratio_d': 0
}

for u in matched:
    row = rowTemp.copy()
    row['uuid'] = u
    row['fieldname'] = df.loc[df[' DSW knowledge model UUID'] == u, "Common standard fieldname\n(click on hyperlinks for descriptions)\n(see GC_RDA DMP structure, here)"].iloc[0]
    for i in range(len(dict['packages'])):
        for e in dict['packages'][i]['events']:
            if e["entityUuid"] == u and e["eventType"] == "AddQuestionEvent":
                row['title'] = e['title']
                row['description'] = e['text']
    row['type'] = "Matched"
    data.append(row)

for u in xlres:
    row = rowTemp.copy()
    row['uuid'] = u
    try:
        row['fieldname'] = df.loc[df[' DSW knowledge model UUID'] == u, "Common standard fieldname\n(click on hyperlinks for descriptions)\n(see GC_RDA DMP structure, here)"].iloc[0]
    except:
        pass
    row['type'] = "In Excel only"
    data.append(row)

for u in dictres:
    row = rowTemp.copy()
    row['uuid'] = u
    for i in range(len(dict['packages'])):
        for e in dict['packages'][i]['events']:
            if e["entityUuid"] == u and e["eventType"] == "AddQuestionEvent":
                row['title'] = e['title']
                row['description'] = e['text']
    row['type'] = "In DSW only"
    data.append(row)

##########################################
# Fuzzy matching between fieldname and title/desc

for row in data:
    if row['fieldname'] != None and (row['title'] != None or row['description'] != None):
        key = row['fieldname'].split("/")[-1] if row['fieldname'].split("/")[-1] != "" else row['fieldname'].split("/")[-2]
        key = key.replace("_", " ")
        try:
            row['ratio_t'] = fuzz.token_set_ratio(key, row["title"])
        except:
            pass
        try:
            row['ratio_d'] = fuzz.token_set_ratio(key, row["description"])
        except:
            pass

##########################################
# Creation of dataframe containing all information

dataframe = pd.DataFrame(data)
dataframe.to_csv("QA.csv")