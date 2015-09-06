from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request, url_for
import json
import os.path
import settings
import collections
from NeuralNetwork import NN
app = Flask(__name__)

SPRING = 0
SUMMER = 1
FALL = 2

CONFIDENCE = ['are confident this class won\'t be offered.', 'are pretty sure this class won\'t be offered.', 'are unsure if this class will be offered.', 'are pretty sure this class will be offered.', 'are confident this class will be offered.']

#settings.py
import os
# __file__ refers to the file settings.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    with open(os.path.join(APP_ROOT, 'data/data.json')) as infile:
       result = json.load(infile)
    return jsonify(result)

@app.route('/courses')
def get_courses():
    with open(os.path.join(APP_ROOT, 'data/autocomplete.json')) as infile:
        result = json.load(infile)
    return jsonify({'response':200, 'data':result})

@app.route('/course', methods=['GET'])
def get_course_information():
    with open(os.path.join(APP_ROOT, 'data/autocomplete.json')) as infile:
        courses = json.load(infile)
    with open(os.path.join(APP_ROOT, 'data/predict.json')) as infile:
        parsed_data = json.load(infile)
    with open(os.path.join(APP_ROOT, 'data/table.json')) as infile:
        table = json.load(infile)
    CONST_SEMESTERS = ['SP', 'SU', 'F']
    CONST_YEARS = map(str, range(2008, 2016))
    if request.args.get('id') in courses:
        course_data = parsed_data[request.args.get('id').upper()]
        pat = []
        found_first = False
        for year in CONST_YEARS:
            for sem in CONST_SEMESTERS:
                if not found_first:
                    if str(year) + ' ' + str(sem) in course_data:
                        found_first = True
                if found_first:
                    entry = []
                    inputs = []
                    if sem == "F":
                        inputs.append(FALL)
                    elif sem == "SP":
                        inputs.append(SPRING)
                    else:
                        inputs.append(SUMMER)
                    print(len(inputs))
                    outputs = []
                    if str(year) + ' ' + str(sem) in course_data:
                        outputs.append(1)
                    else:  
                        outputs.append(0)
                    entry.append(inputs)
                    entry.append(outputs)
                    pat.append(entry)
        n = NN(1, [2, 4, 2], 1)
        n.train(pat, 1000)
        n.test(pat)
        predictions = []
        for sem in range(3):
            predictions.append(n.update([sem])[0])
        course_data = collections.OrderedDict(sorted(course_data.items())) # sort by year, semester
        table = table[request.args.get('id')]
        table = collections.OrderedDict(sorted(table.items())) # sort instructors by name
        for i, prediction in enumerate(predictions):
            if prediction < 0.2:
                predictions[i] = CONFIDENCE[1]
            elif prediction < 0.4:
                predictions[i] = CONFIDENCE[1]
            elif prediction < 0.6:
                predictions[i] = CONFIDENCE[2]
            elif prediction < 0.8:
                predictions[i] = CONFIDENCE[3]
            else:
                predictions[i] = CONFIDENCE[3]
        return render_template('data.html', title=request.args.get('id'), course_data=course_data, table=table, predictions=predictions, semesters=CONST_SEMESTERS, years=CONST_YEARS)
    else:
        return render_template('404.html')    

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 33507))	    
    app.debug = True;
    pp.run(host='0.0.0.0', port=port)
