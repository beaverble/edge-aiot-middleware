import base64
import json
import pandas as pd

file = input("파일명을 입력하시오 : ")
test = pd.read_csv(file,header=None)
test = test.transpose()

json_list = []
json_list1 = []
val = test.values[0][0]
val = val.replace("'", "")
val = val.replace("b","",1)
json_val = json.loads(val)
json_list.append(json_val)

res_payload = json_val['Payload']
dec_res = base64.b64decode(res_payload)
dec_res = dec_res.decode("UTF-8")
str_test = dec_res.replace("'","\"")
json_data = json.loads(str_test)
print("==================================================")
print("첫번째 데이터")
print(json_data)

val1 = test.values[999][0]
val1 = val1.replace("'", "")
val1 = val1.replace("b","",1)
json_val1 = json.loads(val1)
json_list1.append(json_val1)

res_payload = json_val1['Payload']
dec_res = base64.b64decode(res_payload)
dec_res = dec_res.decode("UTF-8")
str_test1 = dec_res.replace("'","\"")
json_data1 = json.loads(str_test1)

print("=================================================")
print("마지막 데이터")
print(json_data1)