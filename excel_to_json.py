from main import areas, resultFolder
import pandas as pd
import json

for area in areas:
    filename = resultFolder + area.get("name") + "-漫展信息.xlsx"
    df_dicts = pd.read_excel(filename, sheet_name=None)
    for sheet in df_dicts.keys():
        df_dicts[sheet] = df_dicts[sheet].to_dict(orient="records")
        # del 0 key in each sheet dict
        for item in df_dicts[sheet]:
            del item[0]
    json.dump(
        df_dicts,
        open(filename.replace(".xlsx", ".json"), "w", encoding="utf-8"),
        ensure_ascii=False,
    )

# save update time in timestamp.txt
import time

with open(resultFolder + "timestamp.txt", "w", encoding="utf-8") as f:
    f.write(str(time.time()))
