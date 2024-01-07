from main import areas, resultFolder
import pandas as pd
import json

for area in areas:
    filename = resultFolder + area.get("name") + "-漫展信息.xlsx"
    df_dicts = pd.read_excel(filename, sheet_name=None)
    for key in df_dicts.keys():
        df_dicts[key] = df_dicts[key].to_dict(orient="records")
    json.dump(
        df_dicts,
        open(filename.replace(".xlsx", ".json"), "w", encoding="utf-8"),
        ensure_ascii=False,
    )
