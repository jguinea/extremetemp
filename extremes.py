import requests, datetime
from metar import Metar
import pandas as pd
from io import StringIO

def fetch_extremes():
    # 1) pull METAR temps
    now  = datetime.datetime.utcnow()
    url  = f"https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{now.hour:02d}Z.TXT"
    lines = requests.get(url).text.splitlines()
    temps = {}
    for line in lines:
        try:
            rpt = Metar.Metar(line)
            if rpt.temp is not None:
                temps[rpt.station_id] = rpt.temp.value("C")
        except:
            continue

    # 2) pull station metadata
    url = "https://www1.ncdc.noaa.gov/pub/data/noaa/isd-history.csv"
    df = pd.read_csv(StringIO(requests.get(url).text), dtype=str)
    df = df.rename(columns={
        "ICAO":"icao","STATION NAME":"name","CTRY":"country",
        "LAT":"lat","LON":"lon"
    })[["icao","name","country","lat","lon"]]
    df = df[df.icao.notna() & df.lat.notna() & df.lon.notna()]
    df.lat = df.lat.astype(float); df.lon = df.lon.astype(float)

    # 3) merge & rank
    df_t = pd.DataFrame.from_dict(temps, orient="index", columns=["temp_C"]) \
             .rename_axis("icao").reset_index()
    df_final = df_t.merge(df, on="icao", how="inner")
    coldest = df_final.nsmallest(1,"temp_C").iloc[0].to_dict()
    hottest = df_final.nlargest(1,"temp_C").iloc[0].to_dict()

    return coldest, hottest