import settings
import os
import json
import re
import collections

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

def main():
    courses = []
    # with open(os.path.join(APP_ROOT, 'data/data_copy_2.json'), 'r') as f:
    with open(os.path.join(APP_ROOT, 'data/data.json'), 'r') as f:
        data = json.load(f)

    aliases = {}
    raw_names = []
    for year in data:
        for semester in data[year]:
            for field in data[year][semester]:
                for level in data[year][semester][field]:
                    for course in data[year][semester][field][level]:
                        raw_course_name = course['title']
                        raw_names.append(raw_course_name)
                        course_name = raw_course_name.strip()
                        course_name = re.sub('[a-z]', '', course_name) # remove lowercase
                        course_name = re.sub('\(.+?\)', '', course_name) # parens
                        course_name = re.sub('  +', ' ', course_name) # multi spaces
                        if(re.match(". [^0-9]", course_name[:3])): # two letter dept name with space in betw
                            course_name = course_name[:1] + course_name[2:]
                        course_name = course_name.strip()
                        courses.append(course_name)
                        aliases[raw_course_name] = course_name
                        print("Added: " + course_name)
    courses_set = set(courses)
    result = []
    for course in courses_set:
        result.append(course)
    result = sorted(result)
    #with open(os.path.join(APP_ROOT, 'data/autocomplete.json'), 'w') as outfile:
    #    json.dump(result, outfile, indent=4)
    with open(os.path.join(APP_ROOT, 'data/raw_course_names.json'), 'w') as outfile:
        json.dump(raw_names, outfile, indent=4)

    """
    {
        course_name : {
            prof : [{(sem, year) : int}]
        }
    }

    """
    meta_data = {}
    for year in data:
        for semester in data[year]:
            for field in data[year][semester]:
                for level in data[year][semester][field]:
                    for course in data[year][semester][field][level]:
                        course_name = aliases[course['title']]
                        if course_name not in meta_data:
                            course_data = {}
                            # meta_data[course_name] = {}
                        else:
                            course_data = meta_data[course_name]

                        semester_symbol = str(semester)[:2].upper()
                        if semester_symbol == 'FA':
                            semester_symbol = 'F'
                        date_pair = str(str(year) + ' ' + str(semester_symbol))

                        for i, section in enumerate(course['sections']):
                            if i is not 0:
                                instructor = str(section['instructor'])
                                if not instructor:
                                    instructor = 'UNLISTED'

                                if instructor not in course_data:
                                    course_data[instructor] = {}
                                if date_pair not in course_data[instructor]:
                                    course_data[instructor][date_pair] = 0
                                course_data[instructor][date_pair] += 1
                
                        meta_data[course_name] = course_data
                        if "CS 378H" in course_name:
                            print(data[year][semester][field][level])
                            print(meta_data[course_name])
    print 'writing: ' + 'table.json'
    #with open(os.path.join(APP_ROOT, 'data/table.json'), 'w') as outfile:
    #    json.dump(meta_data, outfile, indent=4)

    """
    {
        course_name : {
            (sem, year) : {
                prof : {
                    'statuses' : [status], 
                    'score' : score
                    }, 
                   'section_count' : num_sections
                }
            }
    }
    """
    meta_data = {}
    for year in data:
        for semester in data[year]:
            for field in data[year][semester]:
                for level in data[year][semester][field]:
                    for course in data[year][semester][field][level]:

                        course_name = aliases[course['title']]

                        semester_symbol = str(semester)[:2].upper()
                        if semester_symbol == 'FA':
                            semester_symbol = 'F'
                        date_pair = str(str(year) + ' ' + str(semester_symbol))

                        if course_name not in meta_data:
                            meta_data[course_name] = {}

                        if date_pair not in meta_data[course_name]:
                            date_data = {}
                        else:
                            date_data = meta_data[course_name][date_pair]

                        for i, section in enumerate(course['sections']):
                            if i is not 0:
                                instructor = str(section['instructor'])
                                if not instructor:
                                    instructor = 'UNLISTED'

                                status = section['status']

                                if instructor not in date_data:
                                    date_data[instructor] = {'statuses': [], 'score' : 0}

                                date_data[instructor]['statuses'].append(status)

                        date_data[instructor]['section_count'] = len(course['sections']) - 1
                        meta_data[course_name][date_pair] = date_data

    """for course_name in meta_data:
        date_data = meta_data[course_name]
        sorted_date_data = collections.OrderedDict(sorted(date_data.items())) # sort by year, semester
        meta_data[course_name] = sorted_date_data"""

    print 'writing: ' + 'predict.json'
    #with open(os.path.join(APP_ROOT, 'data/predict.json'), 'w') as outfile:
    #    json.dump(meta_data, outfile, indent=4)
    
if __name__ == '__main__':
    main()
