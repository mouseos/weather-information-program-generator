import requests
import json
import datetime
from pytz import timezone
import sys
import re
import wave

from pydub import AudioSegment
from natsort import natsorted
#エリア
area_code=sys.argv[1]
#保存ファイル名
output_file=sys.argv[2]
now = datetime.datetime.now(timezone('Asia/Tokyo')).hour

data = json.loads(requests.get('https://weather.tsukumijima.net/api/forecast/city/'+area_code).text)



#降水確率
precip_prob_today = {
    "T00_06": data["forecasts"][0]["chanceOfRain"]["T00_06"],
    "T06_12": data["forecasts"][0]["chanceOfRain"]["T06_12"],
    "T12_18": data["forecasts"][0]["chanceOfRain"]["T12_18"],
    "T18_24": data["forecasts"][0]["chanceOfRain"]["T18_24"]
}

precip_prob_tomorrow = {
    "T00_06": data["forecasts"][1]["chanceOfRain"]["T00_06"],
    "T06_12": data["forecasts"][1]["chanceOfRain"]["T06_12"],
    "T12_18": data["forecasts"][1]["chanceOfRain"]["T12_18"],
    "T18_24": data["forecasts"][1]["chanceOfRain"]["T18_24"]
}

precip_prob_day_after_tomorrow = {
    "T00_06": data["forecasts"][2]["chanceOfRain"]["T00_06"],
    "T06_12": data["forecasts"][2]["chanceOfRain"]["T06_12"],
    "T12_18": data["forecasts"][2]["chanceOfRain"]["T12_18"],
    "T18_24": data["forecasts"][2]["chanceOfRain"]["T18_24"]
}
precipitation_probability=""
if (now <6):
	precipitation_probability="0時から6時までの降水確率は"+precip_prob_today["T00_06"]+"。6時から12時までは"+precip_prob_today["T06_12"]+"。12時から18時までは"+precip_prob_today["T12_18"]+"。18時から24時までは"+precip_prob_today["T18_24"]+"です。"
elif(now<12):
	precipitation_probability="6時から12時までの降水確率は"+precip_prob_today["T06_12"]+"。12時から18時までは"+precip_prob_today["T12_18"]+"。18時から24時までは"+precip_prob_today["T18_24"]+"です。"
elif(now<18):
	precipitation_probability="12時から18時までの降水確率は"+precip_prob_today["T12_18"]+"。18時から24時までは"+precip_prob_today["T18_24"]+"です。"
elif(now<24):
	precipitation_probability="18時から24時までの降水確率は"+precip_prob_today["T18_24"]+"です。"


def replace_text(text):
    text = re.sub('　', '', text)
    text = re.sub('風', '風。', text)
    text = re.sub('雨', 'あめ', text)
    text = re.sub('所により', '。所により', text)
    return text

today_forecast = "今日は" + replace_text(str(data['forecasts'][0]['detail']['wind'])) + replace_text(str(data['forecasts'][0]['detail']['weather'])) + "でしょう。" + precipitation_probability + "予想最高気温は" + str(data['forecasts'][0]['temperature']['max']['celsius']) + "度です。\n"

tomorrow_forecast = "明日は" + replace_text(data['forecasts'][1]['detail']['wind']) + replace_text(data['forecasts'][1]['detail']['weather']) + "でしょう。" + "0時から6時まで降水確率は" + precip_prob_tomorrow["T00_06"] + "。6時から12時までは" + precip_prob_tomorrow["T06_12"] + "。12時から18時までは" + precip_prob_tomorrow["T12_18"] + "。18時から24時までは" + precip_prob_tomorrow["T18_24"] + "です。" + "予想最高気温は" + data['forecasts'][1]['temperature']['max']['celsius'] + "度。最低気温は" + data['forecasts'][1]['temperature']['min']['celsius'] + "度です。\n"

day_after_tomorrow_forecast = "あさっては" + replace_text(data['forecasts'][2]['detail']['wind']) + replace_text(data['forecasts'][2]['detail']['weather']) + "でしょう。" + "0時から6時まで降水確率は" + precip_prob_tomorrow["T00_06"] + "。6時から12時までは" + precip_prob_tomorrow["T06_12"] + "。12時から18時までは" + precip_prob_tomorrow["T12_18"] + "。18時から24時までは" + precip_prob_tomorrow["T18_24"] + "です。" + "予想最高気温は" + data['forecasts'][2]['temperature']['max']['celsius'] + "度。最低気温は" + data['forecasts'][2]['temperature']['min']['celsius'] + "度です。\n"


#あいさつ
if(4<now and now<10):
	greet="おはようございます。"
	all_forecasts=today_forecast+tomorrow_forecast+day_after_tomorrow_forecast
elif(10<=now and now <16):
	greet="こんにちは。"
	all_forecasts=tomorrow_forecast+day_after_tomorrow_forecast
else:
	greet="こんばんは。"
	all_forecasts=tomorrow_forecast+day_after_tomorrow_forecast


text1=(greet+"""この時間はAIアナウンサーが"""+data['location']['district']+"""の気象情報をお伝えします。まずは、天気概況をお伝えします。
"""+re.sub('雨',"あめ",(data['description']["bodyText"]))+"""それでは"""+data['location']['district']+"""の天気をお伝えします。""")

text2=(data['location']['district']+"の"+all_forecasts+"以上、voicevox、九州そらが気象庁発表の気象情報をお伝えしました。")



def generate_wav(text, speaker,speed, filepath):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    response1=response1.json()
    #速度設定
    response1["speedScale"]=speed
    headers = {'Content-Type': 'application/json',}
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1)
    )

    wf = wave.open(filepath, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(response2.content)
    wf.close()

#辞書機能が動作しないため文字の置き換え
def modify_text(text):
    text = re.sub("明後日","あさって",text)
    text = re.sub("日中","にっちゅう",text)
    text = re.sub("後志","しりべし",text)
    text = re.sub(r"(?<!\d)0%","れいパーセント",text)
    text = re.sub("0時から","れい時から",text)
    text = re.sub("晴れ後","晴れのち",text)
    text = re.sub("くもり後","くもりのち",text)
    text = re.sub("雨後","雨のち",text)
    text = re.sub("雪後","雪のち",text)
    text = re.sub("後志","しりべし",text)
    text = re.sub("弱く","弱く、",text)
    text = re.sub("強く","強く、",text)
    text = re.sub("晴れ未明","晴れ。未明",text)
    text = re.sub("雨未明","雨。未明",text)
    text = re.sub("くもり未明","くもり。未明",text)
    text = re.sub("のち","のち、",text)
    text = re.sub("のち、、","のち、",text)
    return text
text1=modify_text(text1);
text2=modify_text(text2);
#分割しないと結果が返ってこないため分割して結合
print(text1)
print(text2)
generate_wav(text1,16,1.3,"text1.wav")
generate_wav(text2,16,1.3,"text2.wav")
# 2つのwavファイルを読み込む
text1wav = AudioSegment.from_wav("text1.wav")
text2wav = AudioSegment.from_wav("text2.wav")

# wavファイルを連結する
combined = text1wav + text2wav

# 連結されたwavファイルを保存する
combined.export(output_file, format="wav")
