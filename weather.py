import requests
import json
import datetime
import sys
import re
import wave
from pydub import AudioSegment
from natsort import natsorted
#エリア
area=sys.argv[1]
now = datetime.datetime.now().hour

data = json.loads(requests.get('https://weather.tsukumijima.net/api/forecast/city/'+area).text)



#降水確率
cor1=data['forecasts'][0]['chanceOfRain']['T00_06']
cor2=data['forecasts'][0]['chanceOfRain']['T06_12']
cor3=data['forecasts'][0]['chanceOfRain']['T12_18']
cor4=data['forecasts'][0]['chanceOfRain']['T18_24']

#降水確率
cor5=data['forecasts'][1]['chanceOfRain']['T00_06']
cor6=data['forecasts'][1]['chanceOfRain']['T06_12']
cor7=data['forecasts'][1]['chanceOfRain']['T12_18']
cor8=data['forecasts'][1]['chanceOfRain']['T18_24']

#降水確率
cor9=data['forecasts'][2]['chanceOfRain']['T00_06']
cor10=data['forecasts'][2]['chanceOfRain']['T06_12']
cor11=data['forecasts'][2]['chanceOfRain']['T12_18']
cor12=data['forecasts'][2]['chanceOfRain']['T18_24']
cor=""
if (now <6):
	cor="0時から6時までの降水確率は"+cor1+"。6時から12時までは"+cor2+"。12時から18時までは"+cor3+"。18時から24時までは"+cor4+"です。"
elif(now<12):
	cor="6時から12時までの降水確率は"+cor2+"。12時から18時までは"+cor3+"。18時から24時までは"+cor4+"です。"
elif(now<18):
	cor="12時から18時までの降水確率は"+cor3+"。18時から24時までは"+cor4+"です。"
elif(now<24):
	cor="18時から24時までの降水確率は"+cor4+"です。"


#今日の予報
f1="今日は"+re.sub('　','',re.sub('風', '風。', (str(data['forecasts'][0]['detail']['wind']))))+re.sub("雨","あめ",re.sub('　','',re.sub('所により','。所により',str(data['forecasts'][0]['detail']['weather']))))+"でしょう。"+cor+"予想最高気温は"+str(data['forecasts'][0]['temperature']['max']['celsius'])+"度です。\n"
#明日の予報
f2="明日は"+re.sub('　','',re.sub('風', '風。', (data['forecasts'][1]['detail']['wind'])))+re.sub("雨","あめ",re.sub('　','',re.sub('所により','。所により',(data['forecasts'][1]['detail']['weather']))))+"でしょう。"+"0時から6時まで降水確率は"+cor5+"。6時から12時までは"+cor6+"。12時から18時までは"+cor7+"。18時から24時までは"+cor8+"です。"+"予想最高気温は"+data['forecasts'][1]['temperature']['max']['celsius']+"度。最低気温は"+data['forecasts'][1]['temperature']['min']['celsius']+"度です。\n"
#明後日の予報
f3="あさっては"+re.sub('　','',re.sub('風', '風。', (data['forecasts'][2]['detail']['wind'])))+re.sub("雨","あめ",re.sub('　','',re.sub('所により','。所により',(data['forecasts'][2]['detail']['weather']))))+"でしょう。"+"0時から6時まで降水確率は"+cor5+"。6時から12時までは"+cor6+"。12時から18時までは"+cor7+"。18時から24時までは"+cor8+"です。"+"予想最高気温は"+data['forecasts'][2]['temperature']['max']['celsius']+"度。最低気温は"+data['forecasts'][2]['temperature']['min']['celsius']+"度です。\n"

#あいさつ
if(4<now and now<10):
	greet="おはようございます。"
	forecasts=f1+f2+f3
elif(10<=now and now <16):
	greet="こんにちは。"
	forecasts=f2+f3
else:
	greet="こんばんは。"
	forecasts=f2+f3


text1=(greet+"""この時間はAIアナウンサーが"""+data['location']['district']+"""の気象情報をお伝えします。まずは、天気概況をお伝えします。
"""+re.sub('雨',"あめ",(data['description']["bodyText"]))+"""それでは"""+data['location']['district']+"""の天気をお伝えします。""")

text2=(data['location']['district']+"の"+forecasts+"以上、voicevox、九州そらが気象庁発表の気象情報をお伝えしました。")



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
    text = re.sub("[^0123456789]0%","れいパーセント",text)
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
print(text1)
print(text2)
generate_wav(text1,16,1.3,"text1.wav")
generate_wav(text2,16,1.3,"text2.wav")#weather_info_sapporo
# 2つのwavファイルを読み込む
text1wav = AudioSegment.from_wav("text1.wav")
text2wav = AudioSegment.from_wav("text2.wav")

# wavファイルを連結する
combined = text1wav + text2wav

# 連結されたwavファイルを保存する
combined.export("weather_info_sapporo.wav", format="wav")
