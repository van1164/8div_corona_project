from django.shortcuts import render
from .models import 사단
from .models import 여단
from .models import 대대
from .models import 관리자
from .models import 간부
from .models import 질문지
from .models import 문진결과
from .models import 제출여부
import csv
import time
from datetime import date, timedelta
from .forms import EditSurveyForm
import random
import math

#<====================================helper functions======================================>

# flush by time : you can be moved to celery if in need
# flush(id) eradicates all 문진결과 that is over 13 days old
def flush(id):
    dayto = date.today()
    total = 문진결과.objects.filter(owner = 간부.objects.get(id = id)).order_by('date')
    num_total = len(total)
    for result in total: # > means later date
        if date.today() - timedelta(days = 13) > result.date: result.delete() 

# creates random password 
def create_pwd():
    pwd = ""
    for i in range(4):
        pwd += chr(random.randint(33,126)) #vertical bar | vs I vs l !!! needs to be distinguished
    return 'default' + pwd

'''
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
'''
# reads all.csv and get all personal/battalion/brigade/division info : not much of division info tho.
# all.csv should be formatted in the following manner for every person:
#           access, brigade, battalion, person
# ****** note that access must be one of the four: 대대장, 여단장, 사단장, or 간부
#           brigade, battalion, person all expects name of the target
# there is no need to create all battalions, brigades, people separately in django-admin if 
# we set up all.csv with everyone in the division. 
# as it starts reading, whenever it counters a battalion or brigade that has not been initialized
# it will create an object and save to db right away. 
# NOT TESTED
def read_and_extract_csv():
    filename = "all.csv"
    if os.path.exists(filename):
        f = open(filename, "r", encoding = "UTF-8")
        rdr = csv.reader(f)

        # create division
        if len(사단.objects.filter(name = "제8기동사단")) == 0: 
            rising88 = 사단(name = "제8기동사단")
            rising88.save()
        else: rising88 = 사단.objects.get(name = "제8기동사단")
        for name in rdr:
            if name == []: pass
            else: 
                # admin or officer
                # formatting guideline
                # ACCESS, BRIGADE_NAME, BATTALION_NAME, PERSON_NAME
                access = ""
                is_officer = False
                if name[0] == "대대장":
                    access = "Ba"
                elif name[0] == "여단장":
                    access = "Br"
                elif name[0] == "사단장":
                    access = "Di"
                else:
                    is_officer = True
                    access = "None"                 
                
                # create brigade
                brigade = 여단.objects.filter(name = name[1])
                if len(brigade) == 0:
                    new_brig = 여단(name = name[1], division = rising88)
                    new_brig.save()
                    brigade = new_brig
                else: brigade = brigade[0]
                # create battalion
                battalion = 대대.objects.filter(brigade = brigade).filter(name = name[2])
                if len(battalion) == 0:
                    new_batt = 대대(name = name[2], brigade = brigade)
                    new_batt.save()
                    battalion = new_batt
                else: battalion = battalion[0]
                # create person 
                if is_officer:
                    officer = 간부.objects.filter(battalion = battalion).filter(username = name[3])
                    if len(officer) == 0:
                        new_off = 간부(username = name[3], password = create_pwd(),battalion = battalion)
                        new_off.save()
                else:
                    administrator = 관리자.objects.filter(username = name[3]).filter(access_level = access)
                    if len(administrator) == 0:
                        admin = 관리자(username = name[3], password = create_pwd(), access_level = access)
                        admin.save()
    return

'''
now writing csv for each battalion just in case everything needs to be distributed
'''

# get_officer_or_admin returns 1 if admin, -1 if officer, 0 if critical error in system
def get_officer_or_admin(username, password):
    officers = 간부.objects.filter(username = username).filter(password = password)
    admins = 관리자.objects.filter(username = username).filter(password = password)
    if len(officers) == 0 and len(admins) == 0: return 0
    elif len(admins) == 0: return -1
    elif len(officers) == 0: return 1
    else: return 0

# style decider returns class for full progress bar when number of people done equals the total number of people
def style_decider(all, done): 
    if all == done: return "progress-bar bg-success" 
    else: return "progress-bar bg-danger" 

# <========================================= 공통 view ==========================================>

# login handles everyone
def login(request):
    data = {}                                                                       
    curr = request.session.get('username',None)         # get session 
    if curr==None:   #if session does not exist
        return render(request, 'corona/login.html',{})       # render login.html
    else:  # auto login if session exists
        classification = get_officer_or_admin(request.session['username'],request.session['password'])
        return home(request)
        
# home handles both admin and officer login
def home(request):
    data = {}

    # check if it is first time login. We can check this by checking whether there is a session active.
    username = request.session.get('username', None)
    id = request.session.get('id', None)
    password = request.session.get('password', None)
    is_admin = request.session.get('is_admin', False)
    
    # is first time then validate and save to session
    if username == None:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        classification = get_officer_or_admin(username, password)
        if classification == 0: # invalid login
            return render(request, 'corona/login.html', {'re' : True})
        else: # save to session 
            request.session['is_admin'] = is_admin = (classification == 1)
            user = 관리자.objects.filter(username = username).get(password = password) if is_admin else 간부.objects.filter(username = username).get(password = password)
            request.session['id'] = user.id
            request.session['username'] = username
            request.session['password'] = password
    else:
        user = 관리자.objects.get(id = id) if is_admin else 간부.objects.get(id = id)
    data['is_admin'] = is_admin
    data['id'] = user.id
    # handle admin case.
    if is_admin:
        user_access = user.access_level

        # set up variables according to the user.
        already_submitted = False
        num_submitted_target_units= 0
        unit_id = None
        if user_access == "Di":
            # 사단이면 카운트를 할 필요가 없지
            data['done'] = False
            target_units = [1,2,3] # arbitrary list just for line 202 where we set up num_target_units
        elif user_access == "Br":
            already_submitted = len(제출여부.objects.filter(brigade = user.adminofbrig).filter(date = date.today())) != 0
            target_units = 대대.objects.filter(brigade = user.adminofbrig)
            unit_id = user.adminofbrig.id
            # 여단 이면 대대를 카운트해야지
            num_submitted_target_units = 0
            data['brigade_id'] = user.adminofbrig.id
            for target in target_units:
                if len(제출여부.objects.filter(battalion = target).filter(date = date.today())) != 0: num_submitted_target_units += 1
        else:
            already_submitted = len(제출여부.objects.filter(battalion = user.adminofbatta).filter(date = date.today())) != 0
            target_units = 간부.objects.filter(battalion = user.adminofbatta)
            unit_id = user.adminofbatta.id
            data['battalion_id'] = user.adminofbatta.id
            # 대대면 간부들을 카운트해야지
            num_submitted_target_units = len(문진결과.objects.filter(battalion = user.adminofbatta).filter(date = date.today()))     
        num_target_units = len(target_units)
        #set up context for rendering
        data['done'] = not already_submitted and (num_target_units == num_submitted_target_units) 
        data['style_all'] = style_decider(num_target_units, num_submitted_target_units)
        data['access'] = user_access
        data['unit_id'] = unit_id 
        return render(request,'corona/home.html', data)
    else:
        data['officer_id'] = id
        data['done'] = len(문진결과.objects.filter(owner = user).filter(date=date.today())) != 0
        return render(request,'corona/home.html', data)
        
def officer_check(request):
    data = {}

    # grab info from request
    username = request.session['username']
    password = request.session['password']
    id = request.session['id']
    officer_id = request.POST.get('officer_id', None)

    is_officer = request.POST.get('is_officer', False)

    # set up all variables for context
    if is_officer:
        officer = 간부.objects.get(id = id) 
        user = officer
    else: 
        officer = 간부.objects.get(id = officer_id)
        user = 관리자.objects.get(id = id)
    title = officer.username + '의 최근 문진결과'

    # format results for rendering
    results = []
    limit = 13 
    i = 0
    while i < limit:
        day = date.today() - timedelta(days = i)
        result = 문진결과.objects.filter(owner = officer).filter(date =  day)
        if len(result) == 0:
            i += 1
        else:
            questionnaire = result[0].questionnaire.get_dict_all_qs()
            yeses = result[0].get_problematic_qs()
            temp_result = []
            for yes in yeses: temp_result.append(questionnaire['Q' + str(yes)])
            thatday= str(day) +" 체크항목"
            results.append({'result':temp_result, 'date':thatday})
            i += 1
    data['results'] = results
    data['title'] = title
    data['battalion'] = officer.battalion
    data['is_officer'] = is_officer
    data['is_empty'] = len(results) == 0
    return render(request,'corona/officer_check.html', data)

# <=========================================간부 view==============================================>
  
# corona health checklist page
def poll(request):
    data = {}

    #grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']

    # query checklist
    questionnaire = 질문지.objects.filter(ownership = 간부.objects.get(id=id).battalion)[0] 
    questions = questionnaire.get_all_qs()
    
    # format questions for context
    idx = 1
    results = []
    for question in questions:
        results.append({'idx' : idx, 'question' : question, 'name' : 'quest_'+str(idx)})
        idx += 1
    
    # set context for rendering
    data['results'] = results
    data['questionnaire_id'] = questionnaire.id
    return render(request, 'corona/poll.html', data)

# finishing page
def finish(request):
    data = {}
    a = [False] * 10
    a[0] = request.POST.get("quest_1",'2')             
    a[1] = request.POST.get("quest_2", '2')              
    a[2] = request.POST.get("quest_3", '2')
    a[3] = request.POST.get("quest_4", '2')
    a[4] = request.POST.get("quest_5", '2')
    a[5] = request.POST.get("quest_6", '2')
    a[6] = request.POST.get("quest_7", '2')
    a[7] = request.POST.get("quest_8", '2')
    a[8] = request.POST.get("quest_9", '2')
    a[9] = request.POST.get("quest_10", '2')

    # process answers into boolean
    for i in range(10): a[i] = a[i] != '2'
    
    # grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    questionnaire_id = request.POST.get('questionnaire_id')

    flush(id) # get rid of expired results # mark this.

    owner = 간부.objects.get(id = id) # query owner
    am_fine = not any(a)
    questionnaire = 질문지.objects.get(id = questionnaire_id)

    # save result to 문진결과
    result = 문진결과(date = date.today(),A1=a[0], A2=a[1], A3=a[2], A4=a[3],A5=a[4],A6=a[5],A7=a[6],A8=a[7],A9=a[8],A10=a[9], owner = owner, battalion = owner.battalion,is_fine = am_fine, questionnaire = questionnaire)
    result.save()

    # set context for rendering
    data['username'] = username
    data['id'] = id
    data['password'] = password
    
    # set result
    if not am_fine:
        data['result'] = "재택근무"
    else:
        data['result'] = "정상출근"
    return render(request, 'corona/finish.html', data)                                                                               

# <=========================================대대장 view==============================================>

# edit battalion survey
def edit_survey(request):
    data = {}

    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    battalion = 관리자.objects.get(id = id).adminofbatta
    curr = 질문지.objects.get(ownership = battalion)
    curr_qs = []
    idx = 1
    for q in curr.get_all_qs():
        curr_qs.append({
            'q':q,
            'idx':idx
        })
        idx += 1
    data['title'] = battalion.name + ' 문진표 수정'
    data['curr'] = curr_qs
    data['battalion_id'] = battalion.id
    if request.method == 'POST':
        form = EditSurveyForm(request.POST)
        if form.is_valid():
            cleaned_Qs = form.cleaned_data
            if any(cleaned_Qs):
                curr.Q1 = cleaned_Qs['Q1']
                curr.Q2 = cleaned_Qs['Q2']
                curr.Q3 = cleaned_Qs['Q3']
                curr.Q4 = cleaned_Qs['Q4']
                curr.Q5 = cleaned_Qs['Q5']
                curr.Q6 = cleaned_Qs['Q6']
                curr.Q7 = cleaned_Qs['Q7']
                curr.Q8 = cleaned_Qs['Q8']
                curr.Q9 = cleaned_Qs['Q9']
                curr.Q10 = cleaned_Qs['Q10']
                curr.save()
                return batta_check(request)     
        data['re'] = True
        return render(request, 'corona/edit_survey.html', data)
    else:
        form = EditSurveyForm(initial = {
            'Q1': curr.Q1,
            'Q2': curr.Q2,
            'Q3': curr.Q3,
            'Q4': curr.Q4,
            'Q5': curr.Q5,
            'Q6': curr.Q6,
            'Q7': curr.Q7,
            'Q8': curr.Q8,
            'Q9': curr.Q9,
            'Q10': curr.Q10,
        })
        return render(request, 'corona/edit_survey.html', data)

# check status for battalion
def batta_check(request):
    data = {}

    # grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    battalion_id = request.POST.get('battalion_id')

    battalion = 대대.objects.get(id = battalion_id)
    user = 관리자.objects.get(id = id)    # current session user

    battalion_officers = 간부.objects.filter(battalion = battalion)     
    num_officers = len(battalion_officers)
    results = 문진결과.objects.filter(battalion = battalion).filter(date = date.today())
    num_done = len(results)
    normal = results.filter(is_fine = True)
    num_normal = len(normal)
    access = user.access_level
    
    # format 재택근무자 for context
    house_ppl = results.filter(is_fine = False)
    house = []
    idx = 1
    for i in house_ppl:
        house.append({'idx' : idx, 'id': i.owner.id, 'username': i.owner.username })
        idx += 1

    # format 설문실시자 for context
    done = []
    idj = 1
    for j in results:
        done.append({'idx' : idj, 'username': j.owner.username })
        idj += 1

    # format 설문미실시자 for context
    not_finished = []
    idy = 1
    for k in battalion_officers:
        if len(문진결과.objects.filter(owner = k).filter(date = date.today())) == 0:
            not_finished.append({'idx' : idy, 'username':k.username})
            idy += 1
    
    #set up context for rendering
    data['diff'] = [1] * abs(2 * num_done - num_officers)
    data['is_owner'] = is_owner = user.adminofbatta == battalion
    data['brigade_id'] = battalion.brigade.id
    data['danger'] = "card mb-4 py-3 border-bottom-danger"
    data['danger_2'] = "card-body"
    data['danger_3'] = "아직 문진표가 완료되지 않았습니다."
    data['complete'] = num_done == num_officers
    data['not_finished'] = not_finished
    data['done'] = done
    data['house'] = house
    data['style_all'] = style_decider(num_officers, num_done)
    data['permission'] = access != "Ba"  
    data['total'] = num_officers
    data['normal'] = num_normal
    data['home'] = num_done - num_normal
    data['notdone'] = num_officers - num_done
    data['clear'] = True
    data['submitted'] = len(제출여부.objects.filter(date = date.today()).filter(battalion = battalion)) != 0
    data['access'] = access
    if is_owner:
        data['title'] = str(time.localtime().tm_year) +"년 "+ str(time.localtime().tm_mon)+"월 " + str(time.localtime().tm_mday)+"일 "+" 코로나 문진표 현황"
    else:
        data['title'] = battalion.name + " 문진현황"
    # handle zero division case 
    if num_officers == 0:
        data['percentage_done'] = 0
    else:    
        data['percentage_done'] = int(num_done/num_officers * 100)
    if num_done == 0:
        data['percentage_normal'] = 0
    else:
        data['percentage_normal'] = int(num_normal/num_done * 100)
    return render(request,'corona/batta_check.html', data)

# <=========================================여단장 view==============================================>
def brig_check(request):
    data = {}
    
    # grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    brigade_id = request.POST.get('brigade_id')

    brigade = 여단.objects.get(id = brigade_id)
    user = 관리자.objects.get(id =  id)

    # set up variables for context : need to handle 사단장 case
    brigade_battalions = 대대.objects.filter(brigade = brigade) # get all 예하대대s by query
    num_battalions = len(brigade_battalions)

    # query all submissions from 예하대대s
    results = 제출여부.objects.filter(battalion = brigade_battalions[0]).filter(date = date.today())
    for battalion in brigade_battalions:
        results = results | 제출여부.objects.filter(battalion = battalion).filter(date = date.today())
    num_done = len(results)
    access = user.access_level

    # format battalion submissions for context
    battalions = []
    num_house = 0
    num_rest = 1
    for battalion in brigade_battalions:
        submission = results.filter(battalion = battalion)
        check_submission = len(submission) != 0
        if check_submission:
            stats = submission[0].battalion_get_stats()
            num_house = stats['num_house']
            num_rest = stats['num_rest']
        percentage_rest= math.ceil(num_rest/(num_house+num_rest) * 100)
        battalions.append({
            'batta' : battalion, 
            'submitted':check_submission,
            'num_house' : num_house, 
            'num_rest' : num_rest,
            'percentage_rest' : percentage_rest,
            'percentage_house' : 100 - percentage_rest
        })
    
    # set up context for rendering
    data['battalions'] = battalions
    data['is_owner'] = user.adminofbrig == brigade
    data['danger'] = "card mb-4 py-3 border-bottom-danger"
    data['danger_2'] = "card-body"
    data['danger_3'] = "아직 문진표가 완료되지 않았습니다."
    data['complete'] = num_done == num_battalions
    data['style_all'] = style_decider(num_battalions, num_done)
    data['permission'] = access != "Br"
    data['total'] = num_battalions
    data['notdone'] = num_battalions - num_done
    data['title'] = str(time.localtime().tm_year) +"년 "+ str(time.localtime().tm_mon)+"월 " + str(time.localtime().tm_mday)+"일 "+" 코로나 문진표 현황"
    data['percentage_done'] = int(num_done/num_battalions * 100)
    data['submitted'] = len(제출여부.objects.filter(date = date.today()).filter(brigade = brigade)) != 0
    return render(request,'corona/brig_check.html', data)

# <============================================제출 view===============================================>
def submit(request):
    data = {}

    # grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    user = 관리자.objects.get(id =  id)

    # create submission as well as new data
    if user.access_level == "Ba":
        tb_submit = 제출여부(brigade = None, battalion = user.adminofbatta)
    else:
        tb_submit = 제출여부(brigade = user.adminofbrig, battalion = None)
    tb_submit.save()
    
    # set up context for rendering
    return render(request,'corona/submit.html', data)

# <==========================================사단장 view==============================================>
def div_check(request):
    data = {}
    
    # grab info from request
    username = request.session['username']
    id = request.session['id']
    password = request.session['password']
    user = 관리자.objects.get(id =  id)

    # set up variables for context 
    division_brigades = 여단.objects.filter(division = user.adminofdiv) # get all 예하대대s by query
    num_brigades = len(division_brigades)

    # query all submissions from 예하여단s
    results = 제출여부.objects.filter(brigade = division_brigades[0]).filter(date = date.today())
    for brigade in division_brigades:
        results = results | 제출여부.objects.filter(brigade = brigade).filter(date = date.today())
    num_done = len(results)
    access = user.access_level

    # format battalion submissions for context
    brigades = []
    num_house = 0
    num_rest = 1
    for brigade in division_brigades:
        submission = results.filter(brigade = brigade)
        check_submission = len(submission) != 0
        if check_submission:
            stats = submission[0].brigade_get_stats()
            num_house = stats['num_house']
            num_rest = stats['num_rest']
        percentage_rest= math.ceil(num_rest/(num_house+num_rest) * 100)
        brigades.append({
            'brig' : brigade, 
            'submitted':check_submission, 
            'num_house' : num_house, 
            'num_rest' : num_rest,
            'percentage_rest' : percentage_rest,
            'percentage_house' : 100 - percentage_rest
        })
    # set up context for rendering
    data['brigades'] = brigades
    data['danger'] = "card mb-4 py-3 border-bottom-danger"
    data['danger_2'] = "card-body"
    data['danger_3'] = "아직 문진표가 완료되지 않았습니다."
    data['complete'] = num_done == num_brigades
    data['style_all'] = style_decider(num_brigades, num_done)
    data['permission'] = access != "Br"
    data['total'] = num_brigades
    data['title'] = str(time.localtime().tm_year) +"년 "+ str(time.localtime().tm_mon)+"월 " + str(time.localtime().tm_mday)+"일 "+" 코로나 문진표 현황"
    data['percentage_done'] = int(num_done/num_brigades * 100)
    return render(request,'corona/div_check.html', data)