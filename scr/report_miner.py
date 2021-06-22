#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import nltk
import os
import unidecode
import PySimpleGUI as sg
import screens
import json

######### QUERY PARA EXTRAIR OS LAUDOS DO DATA LAKE
'''
SELECT patient_id, accession_number, exame_codigo, exame_desc, CAST(DATE(exam_datetime) AS DATE) AS exam_date, laudo_txt
FROM `interoper-dataplatform-prd.raw_rdi.rdi_tb_carestream_laudos` 
WHERE DATE(exam_datetime) BETWEEN "2021-01-01" AND "2021-06-18"
      
      AND (exame_desc LIKE '%RM%' OR exame_desc LIKE '%RESSONANCIA%')  
      
      AND exame_desc LIKE '%CRANIO%' 
      AND (exame_desc NOT LIKE '%ANGIO%')    
'''


def open_csv(report_file):
    stopwords = nltk.corpus.stopwords.words('portuguese')
    include_stopwords = ['com', 'sem']
    stopwords = [word for word in stopwords if not word in include_stopwords]

    try:
        df = pd.read_csv(report_file, delimiter=',')
    except Exception as e:
        return None

    try:
        drop_columns = ['exame_codigo', 'exame_desc']
        df = df.drop(columns=drop_columns)

        # define qual o nome da coluna do dataframe que contém o laudo
        campo_laudo = 'laudo_txt'

        # aplica a funcao limpa_texto para cada laudo de cada linha do dataframe
        df[campo_laudo] = df.apply(lambda row: limpa_texto(row[campo_laudo]), axis=1)

        # cria uma coluna com os laudos tokenizados.
        # essa funcao pode demorar alguns segundos para processar....
        campo_laudo = 'laudo_txt'
        df['laudo_tokenizado'] = df.apply(lambda row: remove_stopwords(row[campo_laudo]), axis=1)
    except Exception as e:
        sg.Popup(f"Erro ao tentar abrir dataset.\n{e}")
        return None

    return df


def limpa_texto(texto: str):
    # tira a acentuacao do texto. Coração -> Coracao
    texto = unidecode.unidecode(texto)

    # formata o texto para evitar espacos, paragrafos, etc a mais
    texto = replace_string(texto, '*', '')
    texto = replace_string(texto, '..', '.')
    texto = replace_string(texto, '  ', ' ')
    texto = replace_string(texto, ' .', '.')
    texto = replace_string(texto, ' ,', ',')
    texto = replace_string(texto, '( ', '(')
    texto = replace_string(texto, ' )', ')')
    texto = replace_string(texto, ' :', ':')
    texto = replace_string(texto, '\\n', '\n')
    texto = replace_string(texto, '\t', '')
    texto = replace_string(texto, '\n ', '\n')
    texto = replace_string(texto, ' \n', '\n')
    texto = replace_string(texto, '\n.', '\n')
    texto = replace_string(texto, '\n\n\n', '\n\n')
    texto = texto.strip()
    texto = texto.strip('\n')

    # remove o nome do médico radiologista
    texto = remove_doctor_name(texto)

    return texto


def replace_string(texto: str, procurado, substituido: str):
    # procura e troca as strings

    # faz a troca caso o parametro passado for uma string
    if type(procurado) is str:
        while procurado in texto:
            texto = texto.replace(procurado, substituido)
        return texto

    # faz a troca caso o parametro passado for uma lista
    elif type(procurado) is list:
        for palavra in procurado:
            while palavra in texto:
                texto = texto.replace(palavra, substituido)
        return texto


def remove_doctor_name(texto: str):
    # palavras a serem buscadas no texto
    doctor_words = ['\n|Dr.', '\n|Dra.', "\nDr.", "\nDra."]

    # sai procurando pelas palavras de Dr(a).
    for word in doctor_words:
        if word in texto:
            # se encontrou, localizada a posicao
            pos = texto.find(word)
            # faz um slice no texto
            texto = texto[:pos]

    return texto


def lista_frases(texto: str, lista_frases_procuradas: list):
    # gera uma lista de frases quebradas por paragrafo

    lista_return = []

    # splita o texto por paragrafo
    frases_texto = texto.split('\n')

    for frase in frases_texto:
        for procurada in lista_frases_procuradas:
            # se achou o texto procurado na frase
            if procurada.upper() in frase.upper():
                # adiciona o paragrafo na lista de paragrafos encontrados
                lista_return.append(frase)
                break

    if lista_return == []:
        return ''
    else:
        return ' | '.join(lista_return)


def remove_frases(texto: str, lista_frases_procuradas: list):
    lista_return = []
    # Tira o texto da Técnica
    texto = texto.replace('Tecnica:', '')

    # quebra as frases em paragrafos
    texto = texto.replace('. ', '\n')

    # splita o texto em paragrafos
    texto = texto.split('\n')

    for frase in texto:
        # itera cada frase do texto
        flag_remover = False
        for procurada in lista_frases_procuradas:
            if procurada.upper() in frase.upper():
                # se achou, marca como uma frase a remover
                flag_remover = True
                break

        # inclui na lista de frases, apenas aquelas que nao foram marcadas como remover
        if not flag_remover:
            lista_return.append(frase)

    # remonta o laudo apenas com as frases que nao foram removidas
    lista_return = '.\n'.join(lista_return)
    lista_return = limpa_texto(lista_return)

    return lista_return


def contem_frase(texto: str, lista_frases_procuradas: list):
    # checa se uma frase está contida numa lista de frases
    for procurada in lista_frases_procuradas:
        if procurada.upper() in texto.upper():
            return True

    return False


def remove_stopwords(texto: str):
    # garante que todo o conteúdo passado está em formato de lista
    if type(texto) is str:
        lista_texto = [texto]
    elif type(texto) is list:
        lista_texto = texto
    else:
        print("A função remove_stopwords aceita como parâmetro apenas strings ou listas.")
        exit()

    lista_removida = []
    for text in lista_texto:
        # tira a acentuacao
        text = unidecode.unidecode(text)
        # tokeniza o texto tirando as stop words
        text_tokens = nltk.tokenize.word_tokenize(text, language='portuguese')
        tokens_without_sw = [word for word in text_tokens if not word in stopwords]
        tokens_without_sw = ' '.join(tokens_without_sw)
        tokens_without_sw = limpa_texto(tokens_without_sw)
        # insere a frase limpa na lista frases sem stopwords
        lista_removida.append(tokens_without_sw)

    # reconverte a saída para o mesmo formato da entrada
    if type(texto) is str:
        return lista_removida[0]
    elif type(texto) is list:
        return lista_removida


def export_csv(filename):
    try:
        drop_columns = ['laudo_tokenizado', 'laudo_pos_exclusao']
        df_export = df.drop(columns=drop_columns)

        df_export.to_csv(filename, index=False)
        return True
    except Exception as e:
        return e


def save_filter_set(filter, inclusion, exclusion):
    json_filter = {}

    if os.path.isfile(filter_filename):
        try:
            with open(filter_filename, 'r') as f:
                json_filter = json.load(f)
        except:
            pass

    # reorder
    inclusion = '\n'.join(sorted(str(inclusion).strip('\n').split('\n')))
    exclusion = '\n'.join(sorted(str(exclusion).strip('\n').split('\n')))

    json_filter[filter] = {"inclusion": inclusion, "exclusion": exclusion}

    with open(filter_filename, 'w') as f:
        json.dump(json_filter, f, indent=2)

    return True


def delete_filter_set(filter):
    if os.path.isfile(filter_filename):
        try:
            with open(filter_filename, 'r') as f:
                json_filter = json.load(f)

            del json_filter[filter]

            with open(filter_filename, 'w') as f:
                json.dump(json_filter, f, indent=2)

                return True
        except:
            pass

def load_keys_filter_set():
    try:
        with open(filter_filename, 'r') as f:
            json_filter = json.load(f)
        return sorted(list(json_filter.keys()))
    except:
        return []


def load_values_filter_set(filter):
    try:
        with open(filter_filename, 'r') as f:
            json_filter = json.load(f)
        return json_filter.get(filter, {}).get('inclusion', ''), json_filter.get(filter, {}).get('exclusion', '')
    except:
        return '', ''


df = None
stopwords = ''
screen_title = "Report Miner"
filter_filename = 'filters.json'

layout = screens.main_screen(filter_set=load_keys_filter_set())

sg.theme('DarkBlue')
window = sg.Window(screen_title, layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button

    if event == sg.WIN_CLOSED:
        window.close()
        exit(0)

    elif event == "-CSV FILENAME-":
        report_file = values['-CSV FILENAME-']
        if os.path.isfile(report_file):
            if sg.PopupOKCancel(
                    f"\nAbrindo dataset {report_file}\n\nAguarde. Este processo pode levar alguns segundos.\n") == "OK":
                df = open_csv(values['-CSV FILENAME-'])
                if df is not None:
                    novo_nome_arq, _ = os.path.splitext(report_file)
                    novo_nome_arq += "_NEW.csv"
                    window['-EXPORT FILENAME-'].update(novo_nome_arq)
                    sg.Popup(
                        "\nCSV file loaded successfully.\n\nNow, define inclusion and exclusion words and click Process.\n",
                        title=screen_title)

    elif event == "-PROCESS-":
        if df is None:
            sg.Popup("\nSelect your reports dataset before process.\n", title=screen_title)
            continue

        frases_inclusao = str(values['-INCLUSION-']).split('\n')
        frases_exclusao = str(values['-EXCLUSION-']).split('\n')

        frases_inclusao = [f for f in frases_inclusao if f.strip() != '']
        frases_exclusao = [f for f in frases_exclusao if f.strip() != '']

        frases_inclusao = remove_stopwords(frases_inclusao)
        frases_exclusao = remove_stopwords(frases_exclusao)

        # cria uma nova coluna contendo o laudo sem as frases de exclusao
        df['laudo_pos_exclusao'] = df.apply(lambda row: remove_frases(row['laudo_tokenizado'], frases_exclusao), axis=1)

        # cria uma nova coluna contendo apenas as frases de inclusao que foram encontradas no laudo
        df['frases_inclusao'] = df.apply(lambda row: lista_frases(row['laudo_pos_exclusao'], frases_inclusao), axis=1)

        result = '\n'.join(list(df['frases_inclusao'].drop_duplicates().sort_values(ignore_index=True)))
        window['-RESULTS-'].update(result)

    elif event == "-EXPORT CSV-":
        if df is None:
            sg.Popup("\nSelect your reports dataset before process.\n", title=screen_title)
            continue

        report_file = values['-EXPORT FILENAME-']
        status = export_csv(report_file)
        if status == True:
            sg.Popup(f"File {report_file} exported successfully.", title=screen_title)
        else:
            sg.Popup(f"Error exporting to file {report_file} .\n\n{status}", title=screen_title)

    elif event == "-SAVE FILTER-":
        filter = values['-COMBO FILTER-']
        inclusion = values['-INCLUSION-']
        exclusion = values['-EXCLUSION-']

        if save_filter_set(filter=filter, inclusion=inclusion, exclusion=exclusion):
            sg.Popup("\nFilter saved successfully.\n", title=screen_title)
            window['-COMBO FILTER-'].update(value=filter, values=load_keys_filter_set())


    elif event == "-LOAD FILTER-":
        filter = values['-COMBO FILTER-']

        inclusion, exclusion = load_values_filter_set(filter)

        window['-INCLUSION-'].update(inclusion)
        window['-EXCLUSION-'].update(exclusion)

    elif event == "-DELETE FILTER-":
        filter = values['-COMBO FILTER-']

        if delete_filter_set(filter=filter):
            sg.Popup("\nFilter deleted successfully.\n", title=screen_title)
            window['-COMBO FILTER-'].update(value='', values=load_keys_filter_set())