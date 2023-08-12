import json
import requests
from jinja2 import Template
import plotly.graph_objects as go
from datetime import datetime, timedelta, date

# HTML шаблон
theHtml = open('/home/prsem/askolenko_1/askolenko_1/shablon.html', encoding='utf8').read()
shablon = Template(theHtml)

# Данные, необходимые для подсчета статистики
theDate = datetime.now()
Date = theDate.isoformat()
theurl = 'http://94.79.54.21:3000'
thetoken = 'dIlUIIpKrjCcrmmM'
emailEdu = 'askolenko_1@edu.hse.ru'
emailMiem = 'askolenko_1@miem.hse.ru'
beginDate = '2021-09-03'
endDate = '2022-04-01'
myName = 'Коленько Александр Сергеевич'
myGroup = 'БИВ214'
headers = {
    "Content-Type": "application/json"
}


# Git Статистика
def GitStatistics():
    # Запрос данных с сервера
    theResponseGitEdu = requests.post(theurl + r'/api/git/getDataPerWeek', data=json.dumps({
        "studEmail": emailEdu,
        "beginDate": "2022-01-10",
        "endDate": endDate,
        "hideMerge": True,
        "token": thetoken
    }), headers=headers)
    gitResponseEdu = theResponseGitEdu.json()

    # Создание словаря "коммиты", чтобы в дальнейшем построить график
    theCommits = {}
    for i in gitResponseEdu["projects"]:
        if i["name"][:17] == "ivt21-miniproject":
            for j in i["commits_stats"]:
                theCommits[j["beginDate"][:15]] = j["commitCount"]
    return theCommits


def ZulipStatistics():
    # Запрос данных с сервера
    theResponseZulip = requests.post(theurl + r'/api/zulip/getData', data=json.dumps({
        "studEmail": emailMiem,
        "beginDate": beginDate,
        "endDate": endDate,
        "token": "dIlUIIpKrjCcrmmM",
        "timeRange": 1
    }), headers=headers)
    zulipResponse = theResponseZulip.json()

    # Создание словаря "theMessages" и списка "channels". Словарь позволит посроить график,
    # а список выведет кол-во посещенных каналов
    theMessages = {}
    channels = []
    for i in zulipResponse["stats"]:
        if i["messageCount"] != 0:
            theMessages[i["beginDate"][:15].replace(" ", "")] = i["messageCount"]
    for i in zulipResponse["messages"]:
        if i["name"] not in channels:
            channels.append(i["name"])
    channels = "; ".join(channels)
    return theMessages, channels


def JitsiStatistics(theDate):
    # Запрос с сервера пользователя с @edu почтой и с @miem
    theResponseJitsiEdu = requests.post(theurl + r'/api/jitsi/sessions', data=json.dumps({
        "studEmail": emailEdu,
        "beginDate": beginDate,
        "endDate": endDate,
        "beginTime": "09:30:00.000",
        "endTime": "21:00:00.000",
        "token": thetoken,

    }), headers=headers)
    jitsiResponseEdu = theResponseJitsiEdu.json()
    theResponseJitsiMiem = requests.post(theurl + r'/api/jitsi/sessions', data=json.dumps({
        "studEmail": emailMiem,
        "beginDate": beginDate,
        "endDate": endDate,
        "beginTime": "09:30:00.000",
        "endTime": "21:00:00.000",
        "token": thetoken,

    }), headers=headers)

    # Создание словаря "jitsiDates" и списка "jitsiRooms". Словарь позволит посроить график,
    # а список выведет кол-во посещенных комнат
    jitsiRooms = []
    jitsiDates = {}

    jitsiResponseMiem = theResponseJitsiMiem.json()
    for i in jitsiResponseEdu:
        theRoom = i["room"]
        if (theRoom not in jitsiRooms):
            jitsiRooms.append(theRoom)

    for i in jitsiResponseMiem:
        theRoom = i["room"]
        if (theRoom not in jitsiRooms):
            jitsiRooms.append(theRoom)

    jitsiRooms = "; ".join(jitsiRooms)

    # Создание словаря poseshenie для построения графика посещения различных комнат

    # Установка даты начало отчета активности в Jitsi для построения графиков
    beginDateJitsi = date(year=2021, month=10, day=1)
    while beginDateJitsi < date(year=theDate.year, month=theDate.month, day=theDate.day):
        jitsiDates[(beginDateJitsi + timedelta(days=1), beginDateJitsi + timedelta(days=7))] = 0
        beginDateJitsi += timedelta(days=7)
    for i in jitsiResponseMiem:
        dataClass = i["date"].split('-')
        for j in jitsiDates.keys():
            if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                jitsiDates[j] += 1
    for i in jitsiResponseEdu:
        dataClass = i["date"].split('-')
        for j in jitsiDates.keys():
            if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                jitsiDates[j] += 1

    # Создание еще одного словаря для построения графика посещений комнат по Проектному Семинару
    jitsiVisitingPS = {}
    jitsiZanyatiyaPS = {}
    beginDateJitsiPS = date(year=2022, month=1, day=9)
    while beginDateJitsiPS < date(year=theDate.year, month=theDate.month, day=theDate.day):
        jitsiVisitingPS[(beginDateJitsiPS + timedelta(days=1), beginDateJitsiPS + timedelta(days=7))] = 0
        beginDateJitsiPS += timedelta(days=7)
    for i in jitsiResponseMiem:
        dataClass = i["date"].split('-')
        if i["room"] == "ps":
            for j in jitsiVisitingPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiVisitingPS[j] += 1
        elif i["room"] == "ps1":
            for j in jitsiVisitingPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiVisitingPS[j] += 1
    for i in jitsiResponseEdu:
        dataClass = i["date"].split('-')
        if i["room"] == "ps":
            for j in jitsiVisitingPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiVisitingPS[j] += 1
        elif i["room"] == "ps1":
            for j in jitsiVisitingPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiVisitingPS[j] += 1

    beginDateJitsiPSZanatiya = date(year=2022, month=1, day=9)
    while beginDateJitsiPSZanatiya < date(year=theDate.year, month=theDate.month, day=theDate.day):
        jitsiZanyatiyaPS[
            (beginDateJitsiPSZanatiya + timedelta(days=1), beginDateJitsiPSZanatiya + timedelta(days=7))] = 0
        beginDateJitsiPSZanatiya += timedelta(days=7)
    for i in jitsiResponseMiem:
        dataClass = i["date"].split('-')
        if i["room"] == "ps":
            for j in jitsiZanyatiyaPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiZanyatiyaPS[j] = 1
        elif i["room"] == "ps1":
            for j in jitsiZanyatiyaPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiZanyatiyaPS[j] = 1
    for i in jitsiResponseEdu:
        dataClass = i["date"].split('-')
        if i["room"] == "ps":
            for j in jitsiZanyatiyaPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiZanyatiyaPS[j] = 1
        elif i["room"] == "ps1":
            for j in jitsiZanyatiyaPS.keys():
                if j[0] <= date(year=int(dataClass[0]), month=int(dataClass[1]), day=int(dataClass[2])) <= j[1]:
                    jitsiZanyatiyaPS[j] = 1

    # Создание списков недель для проектного семинара и для всех дисциплин для нормальной работы графика
    weeksPS = []
    for i in jitsiVisitingPS:
        weeksPS.append(' from ' + str(i[0]) + ' to ' + str(i[1]))
    weeksPSZanatiya = []
    for i in jitsiZanyatiyaPS:
        weeksPSZanatiya.append(' from ' + str(i[0]) + ' to ' + str(i[1]))
    weeks = []
    for i in jitsiDates.keys():
        weeks.append(' from ' + str(i[0]) + ' to ' + str(i[1]))
    return jitsiRooms, jitsiDates, weeks, weeksPS, jitsiVisitingPS, weeksPSZanatiya, jitsiZanyatiyaPS


def TaigaStatistics():
    theUrlTaiga = 'https://track.miem.hse.ru/api/v1'

    # Необходимое условие отключения нумерации страниц
    dataTaiga = {"x-disable-pagination": "true"}

    # Запрос с сервера задач ЮС
    theTaigaResponseTasks = requests.get(theUrlTaiga + r'/tasks', headers=dataTaiga)
    taigaResponseTasks = theTaigaResponseTasks.json()

    # Создание словаря для построения линейного графика задач
    taigaTasks = {}
    for i in taigaResponseTasks:
        owners_extra_info = i["owner_extra_info"]
        if owners_extra_info["full_name_display"] == 'Александр Коленько':
            if i["subject"] is not None:
                taigaTasks[i["created_date"][:10].replace("-", " ")] = taigaTasks.setdefault(
                    i["created_date"][:10].replace("-", " "), 0) + 1

    # Запрос с сервера ЮС
    theTaigaResponseUS = requests.get(theUrlTaiga + r'/userstories', headers=dataTaiga)
    taigaResponseUS = theTaigaResponseUS.json()
    numberOfUS = 0
    for i in taigaResponseUS:
        theEpic = i["epics"]
        if (theEpic is not None and theEpic[0]["subject"] == "Коленько Александр"):
            numberOfUS += 1
    return numberOfUS, taigaTasks


def Graphics():
    # Получение всех необходимых словарей и списков для построения графиков
    theMessages, channels = ZulipStatistics()
    theCommits = GitStatistics()
    jitsiChannels, jitsiDates, weeks, weeksPS, jitsiVisitingPS, weeksPSZanatiya, jitsiZanyatiyaPS = JitsiStatistics(
        theDate)
    numberOfUS, taigaTasks = TaigaStatistics()

    # Построение всех столбчатых диаграмм
    jitsiBarChart = go.Figure([go.Bar(x=weeks, y=list(jitsiDates.values()))])
    jitsiBarChart.update_layout(yaxis_title="Количество посещений всех дисциплин за неделю", xaxis_title="Недели")
    zulipBarChart = go.Figure([go.Bar(x=list(theMessages.keys()), y=list(theMessages.values()))])
    zulipBarChart.update_layout(yaxis_title="Количество сообщений в данный день", xaxis_title="Дни")
    gitBarChart = go.Figure([go.Bar(x=list(theCommits.keys()), y=list(theCommits.values()))])
    gitBarChart.update_layout(yaxis_title="Количество коммитов за неделю", xaxis_title="Недели")
    jitsiPSBarChart = go.Figure([go.Bar(x=weeksPS, y=list(jitsiVisitingPS.values()))])
    jitsiPSBarChart.update_layout(yaxis_title="Количество посещений комнат 'ps' и 'ps1'", xaxis_title="Недели")
    jitsiZanyatiyaPSBarChart = go.Figure([go.Bar(x=list(weeksPSZanatiya), y=list(jitsiZanyatiyaPS.values()))])
    jitsiZanyatiyaPSBarChart.update_layout(yaxis_title="Количество пар в 'ps' и 'ps1'", xaxis_title="Недели")

    # Получение прирост сообщений/посещений/коммитов/задач на основании полученных данных
    numberofTasks = 0
    for i in taigaTasks.keys():
        numberofTasks += taigaTasks[i]
        taigaTasks[i] = numberofTasks

    visitingPS = 0
    for i in jitsiVisitingPS.keys():
        visitingPS += jitsiVisitingPS[i]
        jitsiVisitingPS[i] = visitingPS

    zanatiyaPS = 0
    for i in jitsiZanyatiyaPS.keys():
        zanatiyaPS += jitsiZanyatiyaPS[i]
        jitsiZanyatiyaPS[i] = zanatiyaPS

    visitings = 0
    for i in jitsiDates.keys():
        visitings += jitsiDates[i]
        jitsiDates[i] = visitings

    commits = 0
    for i in theCommits.keys():
        commits += theCommits[i]
        theCommits[i] = commits

    messages = 0
    for i in theMessages.keys():
        messages += theMessages[i]
        theMessages[i] = messages

    # Построение линейных графиков, а также их обновление для подписания осей абцисс и ординат
    taigaLineal = go.Figure([go.Scatter(x=list(taigaTasks.keys()), y=list(taigaTasks.values()))])
    taigaLineal.update_layout(yaxis_title="Общее количество задач", xaxis_title="Дата")
    jitsiLinealPS = go.Figure([go.Scatter(x=weeksPS, y=list(jitsiVisitingPS.values()))])
    jitsiLinealPS.update_layout(yaxis_title="Общее количество посещений предмета 'Проектный семинар'",
                                xaxis_title="Недели")
    jitsiLinealZanatiyaPs = go.Figure([go.Scatter(x=weeksPSZanatiya, y=list(jitsiZanyatiyaPS.values()))])
    jitsiLinealZanatiyaPs.update_layout(yaxis_title="Общее количество занятий предмета 'Проектный семинар'",
                                        xaxis_title="Недели")
    jitsiLineal = go.Figure([go.Scatter(x=weeks, y=list(jitsiDates.values()))])
    jitsiLineal.update_layout(yaxis_title="Общее количество посещений всех дисциплин", xaxis_title="Недели")
    zulipLineal = go.Figure([go.Scatter(x=list(theMessages.keys()), y=list(theMessages.values()))])
    zulipLineal.update_layout(yaxis_title="Общее количество сообщений",
                              xaxis_title="Дни, в которые были написаны сообщения")
    gitLineal = go.Figure([go.Scatter(x=list(theCommits.keys()), y=list(theCommits.values()))])
    gitLineal.update_layout(yaxis_title="Общее количество коммитов", xaxis_title="Недели")

    # Открытие в файла и написание в нем всех полученных данных и построения графиков
    with open('/var/www/html/students/askolenko_1/askolenko_1.html', 'w') as f:
        f.write(shablon.render(myName=myName, myGroup=myGroup, date=Date, commits=commits, messages=messages,
                               zulipBarChart=zulipBarChart.to_html(), gitBarChart=gitBarChart.to_html(),
                               gitLineal=gitLineal.to_html(), zulipLineal=zulipLineal.to_html(), channels=channels,
                               jitsiChannels=jitsiChannels, visitings=visitings, jitsiBarChart=jitsiBarChart.to_html(),
                               jitsiLineal=jitsiLineal.to_html(), jitsiLinealPS=jitsiLinealPS.to_html(),
                               jitsiPSBarChart=jitsiPSBarChart.to_html(), taigaLineal=taigaLineal.to_html(),
                               numberOfUS=numberOfUS, numberofTasks=numberofTasks,
                               jitsiZanyatiyaPSBarChart=jitsiZanyatiyaPSBarChart.to_html(),
                               jitsiLinealZanatiyaPs=jitsiLinealZanatiyaPs.to_html()))


if __name__ == "__main__":
    Graphics()
