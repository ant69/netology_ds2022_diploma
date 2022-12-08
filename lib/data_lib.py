import pandas as pd
import numpy as np


# Библиотека функций для манипуляций с данными проекта

# Генерация словаря шаблонов протоколов в папке data/intermid
def init_project_dictionaries(echo=False):
    templates_csv = 'data/external/protocols_templates.csv'
    df_templates = pd.read_csv(templates_csv, sep=';')
    df_templates['protocols_df_name'] = df_templates['code'].apply(lambda x: x.replace('П', 'protocols_').replace('.', '_'))
    df_tmpl = df_templates.set_index('code')
    df_tmpl.to_csv('data/intermid/protocols_templates.csv', sep=';')
    if echo:
        print('Шаблон словарей сформирован')
    return df_tmpl    


def load_protocols_data(df_templates):    
    """
    Функция позволяет загрузить все актуальные протоколы по проекту с сайта http://kurators.direktoria.org
    и сохранить протоколы каждого из проектов локально в папке data/external
    Одновременно инициализируются датасеты с протоколами по каждому из шаблонов
    В дальнейшем сохраненные версии датасетов могут скачиваться быстрее из локального хранилища
    """
    prot_mask_csv = 'http://kurators.direktoria.org/action.htm?action=export_data&do=get_template_protocols&filters=a:1:%7Bs:10:%22protocolId%22;s:%LEN_ID%:%22%ID%%22;%7D&format=csv&special=anonim'

    protocols_dfs = []

    for row in df_templates.iterrows():
        prot_id = str(row[1]['id'])
        prot_csv_link = prot_mask_csv.replace('%LEN_ID%', str(len(prot_id))).replace('%ID%', prot_id)
        print(f'Загружаем протокол {row[1]["title"]}')
        prot_df_name = row[1]['protocols_df_name']
        globals()[prot_df_name] = pd.read_csv(prot_csv_link, sep=';')
        globals()[prot_df_name].to_csv('data/external/' + prot_df_name + '_raw.csv', sep=';')
        
        
def load_raw_protocols_data(df_templates):
    """
    Функция позволяет загрузить ранее сохраненные "сырые" протоколы по проекту 
    Инициализируются датасеты с протоколами по каждому из шаблонов
    """
    protocols_dfs = []
    for row in df_templates.iterrows():
        print(f'Загружаем протокол {row[1]["title"]}')
        prot_df_name = row[1]['protocols_df_name']
        globals()[prot_df_name] = pd.read_csv('data/external/' + prot_df_name + '_raw.csv', sep=';')        
        
        

cols_substitutes = {
    'class': ['Параллель класса'],
    'satisfaction': ['Удовлетворенность уроком'],
    'wish_to_change': ['Необходимость изменений'],
    
    'pupils_all': ['Количество учеников на уроке'],
    'pupils_strong': ['Сколько учеников из каждой группы было на уроке::Сильные', 
                    'Количество учеников на уроке::Сильные'],
    'pupils_middle': ['Сколько учеников из каждой группы было на уроке::Средние', 
                    'Количество учеников на уроке::Средние'],
    'pupils_weak': ['Сколько учеников из каждой группы было на уроке::Слабые', 
                  'Количество учеников на уроке::Слабые'],

    'interactions_all': ['Количество ответов на уроке'],
    'interactions_strong': ['Сколько всего взаимодействий было с учениками::Сильные',
                           'Количество ответов на уроке::Сильные',
                           'Количество ответов на уроке от::Сильные'],
    'interactions_middle': ['Сколько всего взаимодействий было с учениками::Средние',
                           'Количество ответов на уроке::Средние',
                           'Количество ответов на уроке от::Средние'],
    'interactions_weak': ['Сколько всего взаимодействий было с учениками::Слабые',
                           'Количество ответов на уроке::Слабые',
                           'Количество ответов на уроке от::Слабые'],
    
    'attention_all': ['Количество отвечавших учеников'],
    'attention_strong': ['Сколько учеников были в зоне внимания учителя::Сильные',
                        'Сколько учеников из каждой группы отвечали::Сильные',
                        'Количество отвечавших учеников::Сильные'],
    'attention_middle': ['Сколько учеников были в зоне внимания учителя::Средние',
                        'Сколько учеников из каждой группы отвечали::Средние',
                        'Количество отвечавших учеников::Средние'],
    'attention_weak': ['Сколько учеников были в зоне внимания учителя::Слабые',
                        'Сколько учеников из каждой группы отвечали::Слабые',
                        'Количество отвечавших учеников::Слабые'],
    
    
    'teacher_comments': ['Выводы и идеи (Вы удовлетворены? Нужно ли что-то изменить? Какую достижимую цель вы хотели бы себе поставить? Понимаете ли вы, как ее достичь?)']
}   


def build_all_protocols_data(df_templates):
    """
    Функция чистки датасетов по каждому из шаблонов протоколов 
    Очищенные от лишних данных датасеты сохраняются в папке data/intermid
    Проводятся следующие преобразования:
    Удаляются вторичные колонки
    Удаляются личные данные
    Заполняются дополнительные колонки с фиксированными названиями параметров.
    Если данные для колонки отсутствуют, устанавливается значение NaN
    Нормализуются данные в колонках satisfaction, wish_of_changes
    """
    
    dfs = []

    for row in df_templates.iterrows():
        print(f'Обрабатываем протокол {row[1]["title"]}')
        prot_df_name = row[1]['protocols_df_name']
        globals()[prot_df_name] = pd.read_csv('data/external/' + prot_df_name + '_raw.csv', sep=';')
        cols = ['Id протокола', 'Код шаблона', 'Дата заполнения', 'Id организации', 
                'Id учителя', 'Id наблюдателя', 'Id куратора']
        new_cols = ['prot_id', 'template_code', 'date_of_lesson', 'org_id', 
                    'teacher_id', 'observer_id', 'curator_id']
        df = globals()[prot_df_name].loc[:, cols]
        df.columns = new_cols
        for cs in cols_substitutes.items():
            old_col = pd.Series(np.nan)
            for raw_col in cs[1]:
                if raw_col in globals()[prot_df_name].columns:
                    old_col = globals()[prot_df_name][raw_col]
            df[cs[0]] = old_col        
        #df.set_index('prot_id', inplace=True)
        df.to_csv('data/intermid/' + prot_df_name + '_stand.csv', sep=';')
        print('-> сохранен файл data/intermid/' + prot_df_name + '_stand.csv')
        dfs.append(df)
        
    df_full = pd.concat(dfs, ignore_index=True)
    
    # Понимая специфику полученных данных, проведу еще несколько преобразований уже готового датасета.
    # 1. Для полей class, satisfaction, wish_to_change заменим значение 0 на NaN
    for col_ in ['class', 'satisfaction', 'wish_to_change']:
        df_full.loc[df_full[col_] == 0, col_] = np.nan

    # 2. Для полей satisfaction, wish_to_change нормализуем значения и округлим
    for col_ in ['satisfaction', 'wish_to_change']:
        df_full[col_] = (df_full[col_] - df_full[col_].min())/(df_full[col_].max() - df_full[col_].min())
        df_full = df_full.round({col_: 3})

    
    df_full.to_csv('data/intermid/full_df_stand.csv', sep=';')  
    print("\n-> Общий файл сохранен data/intermid/full_df_stand.csv")

    return df_full    


def get_core_dataframes():
    """
    Функция возвращает датафрейм со словарем шаблонов и датафрейм со всеми протоколами
    """
    
    df_templates = pd.read_csv('data/intermid/protocols_templates.csv', sep=';') 
    df_main = pd.read_csv('data/intermid/full_df_stand.csv', sep=';') 
    
    return df_templates, df_main