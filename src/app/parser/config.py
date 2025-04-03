timeapiurl = "https://timeapi.io/api/time/current/zone"
timeapiparams = {"timeZone": "Europe/Moscow"}

timetableurl = "https://rgsu.net/for-students/timetable/timetable/novyy-format-den-json.html?filial=%D0%92%D0%A3%D0%97&isNaked=1"
timetableparams = {
    "place": "first",
    "group": "ПИН-Б-0-Д-2022-1",
    "mode": "day",
}

getgrouplisturl = "https://rgsu.net/for-students/timetable/timetable/novyy-format-den-json.html?mode=group&filial=ВУЗ"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
}
