import json


json_array = []
cnt = 1
for row in range(1,500):

    book = {}
    book["S.No"] = cnt
    cnt += 1
  
    book["Book Title"] = "Book title " + str(row)

    book["Author"] = "Book Author " + str(row)
    book["Rent / week"] = 10
    json_array.append(book)


with open("test_csvjson.json", "w", encoding="utf-8") as f:
     json.dump(json_array, f, indent=2, ensure_ascii=False)