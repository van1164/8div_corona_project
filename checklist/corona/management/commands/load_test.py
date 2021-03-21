from django.core.management.base import BaseCommand, CommandError
from corona.models import 관리자, 간부, 대대, 여단, 사단, 제출여부, 문진결과, 질문지
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Creates Load Test Data. Randomization to the max'

    def coinflip(self):
        return bool(random.randint(0,1))

    # create load tester
    def handle(self, *args, **options):
        # initialize each unit
        # division
        division = 사단(name = "ex")
        division.save()
        admin = 관리자(username = 'division', password = "A", access_level= 'Di', adminofdiv= division)
        admin.save()
        # brigade
        admin_name = 'brigade'
        for ___ in range(6):
            example_name = ''
            for _ in range(4): example_name += chr(random.randint(33,126))
            brigade = 여단(name = chr(random.randint(33,126)), division = division)
            brigade.save()
            admin = 관리자(username = 'brigade'+str(___), password = "A", access_level= 'Br', adminofbrig= brigade)
            admin.save()
            if ___ != 0:
                submission = 제출여부(brigade= brigade)
                submission.save()
        # battalion and surveys
        brigades = 여단.objects.all()
        Q1 = 'Q1'
        Q2 = 'Q2'
        Q3 = 'Q3'
        Q4 = 'Q4'
        Q5 = 'Q5'
        Q6 = 'Q6'
        Q7 = 'Q7'
        Q8 = 'Q8'
        Q9 = 'Q9'
        Q10 = 'Q10'
        admin_name = 'battalion'
        for i in range(42):
            example_name = ''
            for _ in range(4): example_name += chr(random.randint(33,126))
            battalion = 대대(name = example_name, brigade = brigades[i%6])
            battalion.save()
            survey = 질문지(ownership = battalion, Q1 = Q1, Q2 = Q2, Q3 = Q3, Q4 = Q4, Q5 = Q5, Q6 = Q6, Q7 = Q7, Q8 = Q8, Q9 = Q9, Q10 = Q10)
            survey.save()
            admin = 관리자(username = 'battalion'+str(i), password = "A", access_level= 'Ba', adminofbatta= battalion)
            admin.save()
            if i > 1:
                submission = 제출여부(battalion = battalion)
                submission.save()
            

        battalions = 대대.objects.all()
        surveys = 질문지.objects.all()
        # people and results
        for i in range(9996):
            flip = self.coinflip()
            temp_name = '간' + str(i)
            battalion = battalions[i%42]
            officer = 간부(username = temp_name, password = 'A', battalion = battalion)
            officer.save()
            for d in range(14):
                result = 문진결과(owner = officer, battalion = battalion, questionnaire = surveys.get(ownership = battalion), date = date.today() - timedelta(days = d), 
                A1= False, A2= False, A3= False, A4= False, A5= False, A6= False, A7= False, A8= False, A9= False, A10= flip, is_fine = not flip)
                result.save()

        #submissions
        officer = 간부(username = 'a', password = 'a', battalion = battalions[0])
        officer.save()

        self.stdout.write(self.style.SUCCESS('Sucessfully added load_data'))