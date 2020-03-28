#!/usr/bin/env python
# coding: utf-8

# In[1]:


from yargy import rule, and_, or_, Parser, not_
from yargy.predicates import gte, lte, in_
from yargy.predicates import gram, is_capitalized, dictionary, normalized, caseless
from yargy.pipelines import morph_pipeline
from datetime import datetime
from yargy.tokenizer import MorphTokenizer
import time
import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()


def extract(text):

    f = open('deseases')
    deseases = f.read()
    deseases = deseases.split('\n')


    text = text.replace('\ufeff', '')
    text = text.replace('\n', ' \n ')
    text = text.replace('\\', ' ')


    symptoms = ['Дата рождения', 'Дата осмотра','Дата заболевания', 'Возраст', 'Болен дней','Болен часов','Возраст в днях','Время поступления', 
                'Время заболевания', 'рост','вес', 'IMT', 'давление диаст', 'давление сист', 'температура поступления','мах температура', 'Т-Ан01', 'Т-Ан03', 
                'пол', 'др заболевания в анамнезе', 'кем направлен', 'побочное действие лекартсв','аллергическая реакция', 'озноб', 'слабость', 'вялость','головная боль', 
                'нарушение сна', 'нарушение аппетита', 'ломота','тошнота', 'нарушение сознания', 'Судороги', 'Парестезии', 'эритема', 
                'с четкими границами', 'валик', 'боль','Гиперемия', 'Отек', 'Лимфаденит', 'Лимфангит', 'квартира, дом','контакт с зараженными','речная рыба','провоцирущие факторы',
                'предрасполагающие факторы','кол-во сопут заболеваний','соц категория','сопутствующий диагноз','основной диагноз', 'контакт с зараженными', 'пищевой анамнез',
               'раневые ворота', 'аллергия на лекарства', 'клещ', 'географический анамнез', 'вредные привычки', 'домашние животные', 'условия труда','избыточное питание',
               'ППТ', 'ЛПТ', 'бытовые условия', 'питание', 'интоксикация', 'ЧСС']

    dict_symp = dict.fromkeys(symptoms)


    # In[5]:


    dates_lst = []

    DAY = and_(
        gte(1),
        lte(31)
    )
    MONTH = and_(
        gte(1),
        lte(12)
    )
    YEAR = and_(
        gte(1),
        lte(19)
    )
    YEARFULL = and_(
        gte(1900),
        lte(2020)
    )
    DATE = or_(
        rule(YEAR,'.',MONTH,'.',DAY),
        rule(DAY,'.',MONTH,'.',YEAR),
        rule(DAY,'.',MONTH,'.',YEARFULL),
        rule(DAY,'.',MONTH),
        rule(DAY,'.',MONTH,YEARFULL),
        rule(DAY,'.',MONTH,YEAR))

    parser = Parser(DATE)
    for match in parser.findall(text):
        dates_lst.append(''.join([_.value for _ in match.tokens]))

    if int(dates_lst[1][-2:])-int(dates_lst[0][-2:])<0:
        dict_symp['Дата рождения'] = dates_lst[0]
        dict_symp['Дата осмотра'] = dates_lst[1]
        dict_symp['Дата заболевания'] = dates_lst[2]
    else: 
        birth = None
        dict_symp['Дата осмотра'] = dates_lst[0]
        dict_symp['Дата заболевания'] = dates_lst[1]

    if len(dict_symp['Дата заболевания'])==5:
        dict_symp['Дата заболевания'] += dict_symp['Дата осмотра'][dict_symp['Дата осмотра'].rfind('.'):]

    TYPE = morph_pipeline(['дней'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))

    if len(lst)>0 and dict_symp['Дата заболевания'] is None:
        dict_symp['Дата заболевания'] = text[lst[0][0][0]-20:lst[0][0][0]+20]
        dict_symp['Дата заболевания'] = re.findall(r'\d+', dict_symp['Дата заболевания'])[0]
        dict_symp['Дата заболевания'] = str(int(dict_symp['Дата осмотра'][:2])-int(dict_symp['Дата заболевания']))
        dict_symp['Дата заболевания'] = dict_symp['Дата заболевания']+dict_symp['Дата осмотра'][2:]



    age_lst = []

    AGE = and_(
        gte(0),
        lte(100)
    )
    AGE_RULE = or_(rule("(",AGE,")"),
                  rule(gram('ADJF'),",",AGE))

    parser = Parser(AGE_RULE)
    for match in parser.findall(text):
        s = ''.join([_.value for _ in match.tokens])
        age_lst.append((re.findall(r'\d+', s)[0]))

    if len(age_lst)>0:
        dict_symp['Возраст'] = age_lst[-1]


    try:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%Y')
    except:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%y')
        d1 = d1.strftime('%d.%m.%Y')
        d1 = datetime.strptime(d1, '%d.%m.%Y')
    try:
        d2 = datetime.strptime(dict_symp['Дата заболевания'], '%d.%m.%Y')
    except:
        d2 = datetime.strptime(dict_symp['Дата заболевания'], '%d.%m.%y')
        d2 = d2.strftime('%d.%m.%Y')
        d2 = datetime.strptime(d2, '%d.%m.%Y')

    dict_symp['Болен дней'] = (d1 - d2).days
    dict_symp['Болен часов'] = (int(dict_symp['Болен дней'])-1)*24



    if dict_symp['Дата рождения'] is None:
        dict_symp['Возраст в днях'] = int(dict_symp['Возраст'])*365
    else:
        d1 = datetime.strptime(dict_symp['Дата осмотра'], '%d.%m.%Y')
        d2 = datetime.strptime(dict_symp['Дата рождения'], '%d.%m.%Y')
        dict_symp['Возраст в днях'] = (d1 - d2).days



    time_lst = []

    HOURS = and_(
        gte(0),
        lte(59)
    )

    MINUTES = and_(
        gte(0),
        lte(59)
    )

    TIME = or_(rule(HOURS,':',MINUTES),
               rule(not(normalized('.')),HOURS, normalized('час')),)

    parser = Parser(TIME)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        s = s.replace('часов', ':00')
        s = s.replace('час', ':00')
        time_lst.append(s)

    if len(time_lst)>0: 
        dict_symp['Время поступления'] = time_lst[0]
        dict_symp['Время заболевания'] = time_lst[0]
    if len(time_lst)>1: 
        dict_symp['Время заболевания'] = time_lst[1]

    t1 = dict_symp['Время поступления']
    t2 = dict_symp['Время заболевания']
    delta = int(t1[:t1.find(':')])+24-int(t2[:t2.find(':')])
    dict_symp['Болен часов'] = dict_symp['Болен часов'] + delta



    HEIGHT = and_(
        gte(50),
        lte(250)
    )
    WEIGHT = and_(
        gte(10),
        lte(150)
    )

    HEIGHT_RULE = or_(rule(normalized('рост'),'-',HEIGHT),
                      rule(normalized('рост'),':',HEIGHT),
                     rule(normalized('рост'),HEIGHT))

    WEIGHT_RULE = or_(rule(normalized('вес'),'-',WEIGHT),
                      rule(normalized('вес'),':',WEIGHT),
                     rule(normalized('вес'),WEIGHT))

    s=''
    parser = Parser(HEIGHT_RULE)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        s = re.findall(r'\d+', s)[0]

    if s != '':
        dict_symp['рост'] = int(s)

    s = ''
    parser = Parser(WEIGHT_RULE)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        s = re.findall(r'\d+', s)[0]

    if s != '':
        dict_symp['вес'] = int(s)

    if (dict_symp['рост'] is not None) and (dict_symp['вес'] is not None):
        dict_symp['IMT'] = round(dict_symp['вес']/(dict_symp['рост']/100*dict_symp['рост']/100),2)




    ADSIST = and_(
        gte(50),
        lte(250)
    )
    ADDIAST = and_(
        gte(20),
        lte(200)
    )

    PRES = or_(rule('АД', ADSIST,'/',ADDIAST),
               rule('АД', ADSIST,ADDIAST),
              rule('АД', ADSIST, ':',ADDIAST),
              rule('АД','-', ADSIST, '/',ADDIAST),
              rule('А/Д', ADSIST, '/',ADDIAST),
              rule('А/Д', ADSIST, ADDIAST),
              rule('А/Д',' ', ADSIST, '/',ADDIAST),
               rule(ADSIST, '/',ADDIAST))

    s = ''
    parser = Parser(PRES)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        s = re.findall(r'\d+', s)

    if len(s)>1:
        dict_symp['давление сист'] = s[0]
        dict_symp['давление диаст'] = s[1]


    PULSE = and_(
        gte(40),
        lte(150)
    )

    PRES = or_(rule('ЧСС','-',PULSE),
               rule('ЧСС',PULSE),
              rule('ЧСС','/',PULSE),
              rule('пульс',PULSE),)

    s = ''
    parser = Parser(PRES)
    for match in parser.findall(text):
        s = (''.join([_.value for _ in match.tokens]))
        s = re.findall(r'\d+', s)

    if len(s)>0:
        dict_symp['ЧСС'] = s[0]


    status = text[text.find('Объективный статус'): text.find('Объективный статус')+text[text.find('Объективный статус')+1:].find(' \n  \n')]

    DEGREES = and_(
        gte(34),
        lte(42)
    )
    SUBDEGREES = and_(
        gte(0),
        lte(9)
    )

    TEMP = or_(rule(DEGREES,',',SUBDEGREES),
               rule(DEGREES,'.',SUBDEGREES),
              rule(DEGREES))

    temp_lst = []
    parser = Parser(TEMP)
    for match in parser.findall(status):
        temp_lst.append(''.join([_.value for _ in match.tokens]))

    if len(temp_lst)>0:
        dict_symp['температура поступления'] = temp_lst[0]

    temp_lst = []
    parser = Parser(TEMP)
    for match in parser.findall(text):
        temp_lst.append(''.join([_.value for _ in match.tokens]))

    if len(temp_lst)>0:
        if dict_symp['температура поступления'] is None:
            dict_symp['температура поступления'] = temp_lst[0]
        dict_symp['мах температура'] = max([float(i.replace(',','.')) for i in temp_lst])



    if dict_symp['мах температура']>38:
        dict_symp['Т-Ан01'] = 1
    else: 
        dict_symp['Т-Ан01'] = 0

    if dict_symp['мах температура']>40:
        dict_symp['Т-Ан03'] = 3
    elif dict_symp['мах температура']>39: 
        dict_symp['Т-Ан03'] = 2
    elif dict_symp['мах температура']>38: 
        dict_symp['Т-Ан03'] = 1
    else:
        dict_symp['Т-Ан03'] = 0



    sex_lst = []
    SEX_RULE = or_(rule(normalized('женский')),
                     rule(normalized('мужской')))

    parser = Parser(SEX_RULE)
    for match in parser.findall(text):
        sex_lst.append(''.join([_.value for _ in match.tokens]))

    dict_symp['пол'] = sex_lst[0]
    dict_symp['пол'] = dict_symp['пол'].lower().replace('женский', '2')
    dict_symp['пол'] = dict_symp['пол'].lower().replace('мужской', '1')


    TYPE = morph_pipeline(deseases[:-1])

    anamnez = text[text.find('Анамнез'): text.find('Анамнез')+text[text.find('Анамнез')+1:].rfind('Анамнез')]
    anamnez = anamnez.replace('туберкулез',' ')
    anamnez = anamnez.replace('туберкулёз',' ')
    family = anamnez[anamnez.find('Семейный'):anamnez.find('Семейный')+60]
    anamnez = anamnez.replace(family,' ')
    anamnez = anamnez.replace('описторхоз',' ')
    dis_lst = []
    parser = Parser(TYPE)
    for match in parser.findall(anamnez):
        dis_lst.append(' '.join([_.value for _ in match.tokens]))

    op_rule = or_(rule(normalized('описторхоз'), not_(normalized('не'))))
    parser = Parser(op_rule)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        dis_lst.append(' описторхоз')

    tub_rule = rule(normalized('туберкулез'), not_(normalized('отрицает')))
    parser = Parser(tub_rule)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        dis_lst.append(' туберкулез')

    dict_symp['др заболевания в анамнезе'] = ', '.join(dis_lst)
    dict_symp['др заболевания в анамнезе'] = morph.parse(dict_symp['др заболевания в анамнезе'])[0].normal_form


    TYPE = morph_pipeline(['Поликлиника',"скорая помощь", "ск/помощь", 'СМП', "обратился"])

    napr = None
    napr_lst = []
    parser = Parser(TYPE)
    for match in parser.findall(text):
        napr_lst.append(' '.join([_.value for _ in match.tokens]))
    if len(napr_lst)>0:
        napr = napr_lst[-1]
        napr = morph.parse(napr)[0].normal_form
    if napr == "обратиться":
        dict_symp['кем направлен'] = 3
    elif napr == "скорая помощь" or napr == "ск/помощь" or napr == 'смп'or napr == "ск / помощь" or napr == "скорой помощь" or napr == "скорую помощь":
        dict_symp['кем направлен'] = 1
    elif napr == "поликлиника":
        dict_symp['кем направлен'] = 2


    ALLERG_RULE = or_(rule(normalized('Аллергическая'),normalized('реакция'), normalized('на'), gram('NOUN').optional().repeatable(), gram('ADJF').optional().repeatable()),
                     rule(normalized('Аллергическая'),normalized('реакция'), normalized('на'), gram('NOUN').optional().repeatable(), gram('ADJF').optional().repeatable(), 
                          '"', gram('ADJF').optional().repeatable(), gram('NOUN').optional().repeatable(), '"'),
                     rule(normalized('Аллергическая'),normalized('реакция'), normalized('на'), gram('NOUN').optional().repeatable(), gram('ADJF').optional().repeatable(),',',
                         gram('NOUN').optional().repeatable(), gram('ADJF').optional().repeatable(),',',gram('NOUN').optional().repeatable(), gram('ADJF').optional().repeatable()),
                     rule(normalized('Аллергическая'),normalized('реакция'), normalized('на'), gram('ADJF').optional(),gram('NOUN').optional().repeatable()))

    parser = Parser(ALLERG_RULE)
    for match in parser.findall(text):
        item = (' '.join([_.value for _ in match.tokens]))
        dict_symp['аллергическая реакция'] = item[item.find('на')+3:]
    if dict_symp['аллергическая реакция'] is not None:
        dict_symp['побочное действие лекартсв'] = 1
        dict_symp['аллергия на лекарства'] = 1


    symptoms = [['озноб', 'познабливание'], 'слабость', 'вялость','головная боль', 'нарушение сна', 'нарушение аппетита', 'ломота',
                'тошнота', 'нарушение сознания','Судороги', 'Парестезии', 'эритема', ['с четкими границами', 'границами четкими' , 
                'четкими неровными краями','с четкими краями', 'краями четкими' , 'четкими неровными краями'], 
                ['валик', 'вал'], 'боль',['Гиперемия', 'гиперемирована'], 'Отек', 'Лимфаденит', 'Лимфангит']

    for i in symptoms:
        lst = []
        if isinstance(i, str):
            TYPE = morph_pipeline([i])
        else:
            TYPE = morph_pipeline(i)

        parser = Parser(TYPE)
        for match in parser.findall(text):
            lst.append(' '.join([_.value for _ in match.tokens]))
        if len(lst)>0:
            if isinstance(i, str):
                dict_symp[i]=1
            else:
                dict_symp[i[0]]=1
        else:
            if isinstance(i, str):
                dict_symp[i]=0
            else:
                dict_symp[i[0]]=0


    # In[20]:


    TYPE = morph_pipeline(['географический', 'выезжал'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-40:match.span[1]+40]
        geo_rule = rule(not_(normalized('не')),normalized('выезжал'))
        parser = Parser(geo_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['географический анамнез'] = 1
        else:
            dict_symp['географический анамнез'] = 0



    TYPE = morph_pipeline(['бытовые'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-30:match.span[1]+30]
        cond_rule = rule(not_(normalized('не')),normalized('удовлетворительные'))
        parser = Parser(cond_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['бытовые условия'] = 1
        else:
            dict_symp['бытовые условия'] = 0



    TYPE = morph_pipeline(['условия труда'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-20:match.span[1]+20]
        cond_rule = rule(not_(normalized('не')),normalized('удовлетворительные'))
        parser = Parser(cond_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['условия труда'] = 1
        else:
            dict_symp['условия труда'] = 0


    TYPE = morph_pipeline(['питание'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-20:match.span[1]+20]
        food_rule = or_(rule(not_(normalized('не')),normalized('удовлетворительное')),
                       rule(not_(normalized('не')),normalized('полноценное')))
        parser = Parser(food_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['питание'] = 1
        else:
            dict_symp['питание'] = 0

        food_rule = rule(not_(normalized('не')),normalized('избыточное'))
        parser = Parser(food_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['избыточное питание'] = 1
        else:
            dict_symp['избыточное питание'] = 0


    TYPE = morph_pipeline(['рыба'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-40:match.span[1]+40]
        TYPE = morph_pipeline(['да', 'постоянно'])
        parser = Parser(TYPE)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['речная рыба'] = 1
        fish_rule = rule(not_(normalized('не')),normalized('употребляет'))
        parser = Parser(fish_rule)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['речная рыба'] = 1
        else:
            dict_symp['речная рыба'] = 0


    TYPE = morph_pipeline(['контакт'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-40:match.span[1]+40]
        TYPE = morph_pipeline(['да'])
        parser = Parser(TYPE)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['контакт с зараженными'] = 1
        else:
            dict_symp['контакт с зараженными'] = 0



    lst = []
    TYPE = morph_pipeline(['рана', "раневые ворота", "входные ворота"])

    parser = Parser(TYPE)
    for match in parser.findall(text):
        lst.append(' '.join([_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp["раневые ворота"] = 1
    else:
        dict_symp["раневые ворота"] = 0



    lst = []
    TYPE = morph_pipeline(['интоксикация'])

    parser = Parser(TYPE)
    for match in parser.findall(text):
        lst.append(' '.join([_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp["интоксикация"] = 1
    else:
        dict_symp["интоксикация"] = 0



    lst = []
    TYPE = morph_pipeline(['клещ', "присасывание"])

    parser = Parser(TYPE)
    for match in parser.findall(text):
        lst.append(' '.join([_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp["клещ"] = 1
    else:
        dict_symp["клещ"] = 0


    TYPE = morph_pipeline(['сырой воды'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-80:match.span[1]+80]
        TYPE = morph_pipeline(['не было', 'отрицает', 'нет'])
        parser = Parser(TYPE)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['пищевой анамнез'] = 0
        else:
            dict_symp['пищевой анамнез'] = 1



    TYPE = morph_pipeline(['вредные привычки', 'алкоголь'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        text_fish = text[match.span[1]-80:match.span[1]+80]
        TYPE = morph_pipeline(['не было', 'отрицает', 'нет', 'не употребляет'])
        parser = Parser(TYPE)
        lst = []
        for match in parser.findall(text_fish):
            lst.append((match.span, [_.value for _ in match.tokens]))
        if len(lst)>0:
            dict_symp['вредные привычки'] = 0
        else:
            dict_symp['вредные привычки'] = 1

    smoke_rule = or_(rule(not_(normalized('не')),normalized('курит')),
                    rule(not_(normalized('не')),normalized('употребляет')))
    parser = Parser(smoke_rule)
    lst = []
    for match in parser.findall(text_fish):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp['вредные привычки'] = 1


    home = None
    home_types = [['бездомный'],
                   ['дом благоустроенный'],
                   ['дом не благоустроенный','дом неблагоустроенный'],
                   ['квартира не благоустроенная', 'квартира неблагоустроенная'],
                   ['квартира благоустроенная'],]

    for i in range(len(home_types)):
        home_lst = []
        TYPE = morph_pipeline(home_types[i])
        parser = Parser(TYPE)
        for match in parser.findall(text):
            home_lst.append(' '.join([_.value for _ in match.tokens]))
        if len(home_lst)>0:
            home = i

    dict_symp['квартира, дом'] = home


    pets = []
    pet_types = [['кошка'],
                   ['собака'],
                   ['корова','коза']]

    for i in range(len(pet_types)):
        pet_lst = []
        TYPE = morph_pipeline(pet_types[i])
        parser = Parser(TYPE)
        for match in parser.findall(text):
            pet_lst.append(' '.join([_.value for _ in match.tokens]))
        if len(pet_lst)>0:
            pets.append(i+1)

    if len(pets)>1:
        pets = 4
    elif len(pets)>0:
        pets = pets[0]
    else:
        pets = 0
    dict_symp['домашние животные'] = pets


    factors = []
    factor_types = [['ссадины',"царапины", "раны", "расчесы", "уколы", "потертости", "трещины", 'вскрытие'],
                   ['ушибы'],
                   ['переохлаждение','перегревание','смена температуры'],
                   ['инсоляция'],
                   ['стресс'],
                   ['переутомление']]

    for i in range(len(factor_types)):
        factor_lst = []
        TYPE = morph_pipeline(factor_types[i])
        parser = Parser(TYPE)
        for match in parser.findall(text):
            factor_lst.append(' '.join([_.value for _ in match.tokens]))
        if len(factor_lst)>0:
            factors.append(i+1)

    dict_symp['провоцирущие факторы'] = factors


    factors = []
    factor_types = [['микоз',"диабет", "ожирение", "варикоз", "недостаточность", "лимфостаз", "экзема"],
                   ['тонзилит',"отит", "синусит", "кариес", "пародонтоз", "остеомиелит", "тромбофлебит", "трофические язвы"],
                   ['резиновая обувь','загрязнения кожных'],
                   ['соматические заболевания']]

    for i in range(len(factor_types)):
        factor_lst = []
        TYPE = morph_pipeline(factor_types[i])
        parser = Parser(TYPE)
        for match in parser.findall(text):
            factor_lst.append(' '.join([_.value for _ in match.tokens]))
        if len(factor_lst)>0:
            factors.append(i+1)

    dict_symp['предрасполагающие факторы'] = factors


    lst = []
    TYPE = morph_pipeline(['работает'])
    parser = Parser(TYPE)
    for match in parser.findall(text):
        lst.append(' '.join([_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp['соц категория'] = 0

    soc_rule = rule(not_(normalized('не')),normalized('работает'))
    parser = Parser(soc_rule)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp['соц категория'] = 1


    DIAGNOZ_RULE = or_(rule(normalized('сопутствующий'), not_(or_(gram('NOUN')))),
                      rule(normalized('сопутствующий'),normalized('диагноз')),
                      rule(normalized('диагноз'),normalized('сопутствующий')),)

    rules = ['сопутствующий', 'сопутствующий диагноз', 'диагноз сопутствующий']
    TYPE = morph_pipeline(rules)
    parser = Parser(DIAGNOZ_RULE)
    lst = []
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        dict_symp['сопутствующий диагноз'] = text[match.span[1]+2:match.span[1]+text[match.span[1]:].find(' \n  \n')]
        dict_symp['кол-во сопут заболеваний'] = dict_symp['сопутствующий диагноз'].count('\n')
        if dict_symp['кол-во сопут заболеваний']==0: dict_symp['кол-во сопут заболеваний']=1


    DIAGNOZ_RULE = or_(rule(normalized('диагноз'),normalized('при'),normalized('поступлении')),
                       rule(normalized('клинический'),normalized('диагноз')),
                       rule(normalized('диагноз'),normalized('клинический')),
                      rule(normalized('основной'),normalized('диагноз')),
                      rule(normalized('диагноз'),normalized('основной')),
                       rule(normalized('Ds')),
                      rule(not_(or_(gram('ADJF'),gram('NOUN'))),normalized('диагноз'),not_(or_(gram('ADJF'),gram('PREP')))))

    lst = []
    parser = Parser(DIAGNOZ_RULE)
    for match in parser.findall(text):
        lst.append((match.span, [_.value for _ in match.tokens]))
    last = match.span[1]+text[match.span[1]:].find(' \n  \n')
    if last == match.span[1]-1:
        last = len(text)-1
    dict_symp['основной диагноз'] = text[match.span[1]+1:last]


    # In[38]:


    TYPE = morph_pipeline(['левая', 'слева'])
    parser = Parser(TYPE)
    lst = []
    for match in parser.findall(dict_symp['основной диагноз']):
        lst.append((match.span, [_.value for _ in match.tokens]))

    TYPE = morph_pipeline(['правая', 'справа'])
    parser = Parser(TYPE)
    for match in parser.findall(dict_symp['основной диагноз']):
        lst.append((match.span, [_.value for _ in match.tokens]))

    part = dict_symp['основной диагноз']
    if len(lst) == 0:
        parser = Parser(DIAGNOZ_RULE)
        for match in parser.findall(text):
            lst.append((match.span, [_.value for _ in match.tokens]))
        match = lst[0][0][1]
        last = match+text[match:].find(' \n  \n')
        if last == match-1:
            last = len(text)-1
        dict_symp['основной диагноз'] = text[match+1:last]
        part = text[text.find('Диагноз'):]


    TYPE = morph_pipeline(['левая', 'слева'])
    parser = Parser(TYPE)
    left_rozha = []
    lst = []
    rozha_types = [['волосистая часть головы', 'волостистой части головы'], ['лицо', "ушная раковина"],
                   ['нос','губы'],['верняя часть туловища', 'верхняя конечность'],['нижняя часть туловища'],
                   ['пах', 'половые органы'],['верняя часть спины'],['нижняя часть спины'],
                   ['плечо'],['предплечье'],['кисть'],['бедро'],['голень'],['стопа'],['голеностоп']]

    for match in parser.findall(part):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        for i in range(len(rozha_types)):
            rozha_lst = []
            TYPE = morph_pipeline(rozha_types[i])
            parser = Parser(TYPE)
            for match in parser.findall(part):
                rozha_lst.append(' '.join([_.value for _ in match.tokens]))
            if len(rozha_lst)>0:
                left_rozha.append(i+1)
    dict_symp['ЛПТ'] = left_rozha

    TYPE = morph_pipeline(['правая', 'справа'])
    parser = Parser(TYPE)
    right_rozha = []
    lst = []
    for match in parser.findall(part):
        lst.append((match.span, [_.value for _ in match.tokens]))
    if len(lst)>0:
        for i in range(len(rozha_types)):
            rozha_lst = []
            TYPE = morph_pipeline(rozha_types[i])
            parser = Parser(TYPE)
            for match in parser.findall(part):
                rozha_lst.append(' '.join([_.value for _ in match.tokens]))
            if len(rozha_lst)>0:
                right_rozha.append(i+1)
    dict_symp['ППТ'] = right_rozha

    return dict_symp