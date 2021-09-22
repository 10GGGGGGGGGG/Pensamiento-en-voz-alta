import moviepy.editor as mp
import requests
import re
import unidecode
import pandas as pd

keywords = {
    'mir[a|o|e] al frente': 'FV',
    'mir[a|o|e] a la izquierd[o|a]|mir[a|o|e] la izquierd[o|a]': 'LV',
    'mir[a|o|e] a la derech[o|a]|mir[a|o|e] la derech[o|a]': 'RV',
    'gir[a|o|e] a la derech[o|a](?! y)': 'SW-TR-R',
    'gir[a|o|e] a la derech[o|a] y rectific[a|o]': 'SW-TR-S',
    'gir[a|o|e] a la izquierd[o|a](?! y)': 'SW-TL-R',
    'gir[a|o|e] a la izquierd[o|a] y rectific[a|o]': 'SW-TL-S',
    'pong[o|a] intermitente izquierd[o|a]': 'LB-ON',
    'quit[o|a|e] intermitente izquierd[o|a]': 'LB-OFF',
    'pong[o|a] intermitente derech[o|a]': 'RB-ON',
    'quit[o|a|e] intermitente derech[o|a]': 'RB-OFF',
    'pis[o|a|e] embrag(?:ue|a|o)': 'G-ON',
    'suelt[o|a] embrag(?:ue|a|o)': 'G-OFF',
    'sub[a|o|e] march[a|o|e]': 'GU',
    'baj[a|o|e] march[a|o|e]': 'GD',
    'pis[a|e|o] acelerador[a-z]*': 'T-ON',
    'suelto[o|a] acelerador[a-z]*': 'T-OFF',
    'pis[a|e|o] fren[a|e|o]': 'B-ON',
    'suelt[o|a] fren[a|e|o]': 'B-OFF'
}

# Añadir tambien esta inicializacion del dataframe al nuevo codigo
result_table_dataframe = pd.DataFrame(data={
    'Categoría': ['Vista', 'Vista', 'Vista',
                  'Manos', 'Manos', 'Manos', 'Manos', 'Manos', 'Manos', 'Manos', 'Manos',
                  'Pies', 'Pies', 'Pies', 'Pies', 'Pies', 'Pies', 'Pies', 'Pies'],

    'Acción': ['Mirar al frente', 'Mirar a la izquierda', 'Mirar a la derecha', 'Girar a la derecha',
               'Girar a la derecha y rectificar', 'Girar a la izquierda',
               'Girar a la izquierda y rectificar', 'Poner el intermitente izquierdo', 'Quitar el intermitente izquierdo',
               'Poner el intermitente derecho', 'Quitar el intermitente derecho', 'Pisar embrague', 'Soltar embrague',
               'Subir marcha', 'Bajar marcha', 'Pisar acelerador', 'Soltar acelerador', 'Pisar freno', 'Soltar freno'],

    'Código': ['FV', 'LV', 'RV', 'SW-TR-R', 'SW-TR-S', 'SW-TL-R', 'SW-TL-S', 'LB-ON', 'LB-OFF', 'RB-ON', 'RB-OFF',
               'G-ON', 'G-OFF', 'GU', 'GD', 'T-ON', 'T-OFF', 'B-ON', 'B-OFF'],

    'Nº de veces dicho': 0
}
)


def transform_video_to_audio(video_path, audio_path):
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)


def speech_to_text_converter(audio, headers):
    response = requests.post('https://api.eu-de.speech-to-text.watson.cloud.ibm.com/instances/fa66ae49-0014-4933-a5de-03af9c450a6b/v1/recognize?model=es-ES_NarrowbandModel&timestamps=true&background_audio_suppression=0.3',
                             headers=headers,
                             data=audio,
                             auth=('apikey', 'o_NQM_Wbr2hUwteQzfW2keB9dxTEmdV6I4Dw4_FEUyKU'))
    result = response.json()
    transcript = []
    for chunck_text in result['results']:
        transcript.extend(chunck_text['alternatives'][0]['timestamps'])
    transcript = [tuple(element[:-1]) for element in transcript]
    return transcript


def get_full_text(transcript):
    full_text = ''
    for text in transcript:
        full_text += text[0] + ' '

    return full_text


# Metodo cambiado, para que en esta ocasion devuelva el dataframe con el numero de veces que aparece un codigo dicho
def add_keywords(text):
    keywords_dict = {}
    text = unidecode.unidecode(text)
    if '#' in text:
        text = re.sub(r'#(.*?)#', '', text)
    for keyword, value in keywords.items():
        try:
            text = re.sub(r'({keyword})'.format(keyword=keyword),
                          r'\1 <b><font color="blue">#{value}#</font></b>'.format(value=value), text)
            keywords_found = re.findall(
                r'({keyword})'.format(keyword=keyword), text)
            keywords_dict[value] = len(keywords_found)
        except:
            print('keyword not found')

    result_table_dataframe['Nº de veces dicho'] = result_table_dataframe['Código'].apply(
        lambda key: keywords_dict[key])

    return text, result_table_dataframe
