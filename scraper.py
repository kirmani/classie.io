import urllib
import urllib2
from bs4 import BeautifulSoup
import cookielib
import requests
from requests import session
import json

#settings.py
import os
# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

rootURL = "http://registrar.utexas.edu/"


CONST_LEVELS = ['L', 'U', 'G']

def main():
    years_links = {}
    for year in range(2013, 2015):
        years_links[year] = (getSchedulesForYear(year))
    years_links[2015] = {}
    years_links[2015]['spring'] = "http://registrar.utexas.edu/schedules/152/"
    years_links[2015]['summer'] = "http://registrar.utexas.edu/schedules/156/"
    years_links[2015]['fall'] = "http://registrar.utexas.edu/schedules/159/"

    # if not os.path.exists(os.path.join(APP_ROOT, 'data/data.json')):
    #     data = {}
    # else:
    with open(os.path.join(APP_ROOT, 'data/data.json'), 'r') as f:
        data = json.load(f)
        # print(data)
    fields = []
    for year in years_links:
        if year not in data:
            data[year] = {}
        for semester in years_links[year]:
            if semester not in data[year]:
                data[year][semester] = {}
            fieldLink = getFieldsLink(years_links[year][semester])
            fields = getFields(fieldLink)
            # print (fields)
            for field in fields:
                if field['id'] not in data[year][semester]:
                    data[year][semester][field['id']] = {}
                    for level in CONST_LEVELS:
                        data[year][semester][field['id']][level] = {}
                        print("Getting " + field['id'] + " "  + level + " classes in year " + str(year) + "...")
                        courses = getCourses(fieldLink, field['id'], level)
                        data[year][semester][field['id']][level] = courses
                        # dumps page information to json file
                        with open(os.path.join(APP_ROOT, 'data/data.json'), 'w') as outfile:
                                json.dump(data, outfile, indent=4)
                else:
                    print(field['id'] + " for " + str(year) + " already submitted...")

def login(coursesLink):
    # Input parameters we are going to send
    payload = {
        'IDToken1': 'sk35375',
        'IDToken2': '$eAn12345'
    }
    c = requests.session()
    c.post('https://login.utexas.edu/openam/UI/Login', data=payload)
    response = c.get(coursesLink)
    # print(response.text)

    s = requests.session()
    soup = BeautifulSoup(response.text)
    token = ""
    for n in soup('input'):
        if n.get('name','') == 'LARES':
            token = n['value']


    auth = {
        'LARES': token
    }
    s.post(coursesLink, auth)
    return s

def getCourses(coursesLink, field, level):
    s = login(coursesLink)
    response = s.get("https://utdirect.utexas.edu/apps/registrar/course_schedule/" + coursesLink[len(coursesLink) - 5:] + "/results/?fos_fl=" + field + "&level=" + level + "&search_type_main=FIELD")
    courses = []
    soup = BeautifulSoup(response.text)
    hasNextPage = True
    while hasNextPage:
        for table in soup.find_all('table'):
            table_class = table.get('class','')
            if "rwd-table" in table_class:
                class_count = 0
                course = {}
                course['sections'] = []
                for tr in table.find_all('tr'):
                    for td in tr.find_all('td'):
                        td_class = td.get('class','')
                        if "course_header" in td_class:
                            if count is not 0:
                                courses.append(course)
                            course = {}
                            course['title'] = tr.get_text().strip()
                            course['sections'] = []
                            # print("DEBUG")
                            class_count += 1
                    else:
                        count = 0
                        section = {}
                        for td in tr.find_all('td'):
                            if count is 0:
                                section['unique'] = td.get_text()
                            elif count is 1:
                                section['days'] = []
                                for span in td.find_all('span'):
                                    section['days'].append(span.get_text())
                            elif count is 2:
                                section['hours'] = []
                                for span in td.find_all('span'):
                                    section['hours'].append(span.get_text())
                            elif count is 3:
                                section['room'] = []
                                for span in td.find_all('span'):
                                    section['room'].append(span.get_text())
                            elif count is 4:
                                section['instructor'] = td.get_text()
                            elif count is 5:
                                section['status'] = td.get_text()
                            count += 1
                        course['sections'].append(section)
        # print("Page recorded")
        hasNextPage = False
        for a in soup.find_all('a'):
            a_class = a.get('id','')
            count = 0
            if "next_nav_link" in a_class and count is 0:
                hasNextPage = True
                response = s.get("https://utdirect.utexas.edu/apps/registrar/course_schedule/20159/results/" + a.get('href',''))
                soup = BeautifulSoup(response.text)
                # print(courses)
                count += 1
    return courses


def getFields(coursesLink):
    s = login(coursesLink)
    response = s.get("https://utdirect.utexas.edu/apps/registrar/course_schedule/" + coursesLink[len(coursesLink) - 5:])
    # print(response.text)

    soup = BeautifulSoup(response.text)
    fields = []
    for select in soup.find_all('select'):
        select_id = select.get('id','')
        if "fos_fl" in select_id:
            for option in select.find_all('option'):
                option_value = option.get('value','')
                if option_value is not '""':
                    fields.append({'id':option_value, 'title':option.get_text()})
    return fields

def getFieldsLink(yearLink):
    url = yearLink
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)

    for div in soup.find_all('div'):
        div_class = div.get('class','')
        if "gobutton" in div_class:
            for a in div.find_all('a'):
                return a.get('href')


def getSchedulesForYear(year):
    url = "http://registrar.utexas.edu/schedules/archive"
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)

    semester_to_link = {}

    for div in soup.find_all('div'):
        div_class = div.get('class','')
        if "callout2" in div_class:
            for a in div.find_all('a'):
                a_text = a.get_text()
                if str(year) in a_text:
                    if "fall" in a_text:
                        semester_to_link['fall'] = rootURL + a.get('href')
                    elif "spring" in a_text:
                        semester_to_link['spring'] = rootURL + a.get('href')
                    elif "summer" in a_text:
                        semester_to_link['summer'] = rootURL + a.get('href')
    return semester_to_link



if __name__ == '__main__':
    main()
