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
        officers = 간부.objects.all()
        # people and results
        for officer in officers:
            flip = self.coinflip()
            battalion = officer.battalion
            if officer.password != 'a':
                result = 문진결과(owner = officer, battalion = battalion, questionnaire = surveys.get(ownership = battalion), date = date.today(), A1= False, A2= False, A3= False, A4= False, A5= False, A6= False, A7= False, A8= False, A9= False, A10= flip, is_fine = not flip)
                result.save()
            else: 
                special_officer = officer
                special_battalion = officer.battalion
                special_brigade = special_battalion.brigade
                brigades = 여단.objects.all()
                battalions = 대대.objects.all()
                for brigade in brigades:
                    if brigade != special_brigade:
                        submission = 제출여부(brigade= brigade)
                        submission.save()
                for battalion in battalions:
                    if battalion != special_battalion:
                        submission = 제출여부(battalion = battalion)
                        submission.save()
        self.stdout.write(self.style.SUCCESS('Sucessfully added today_load_data'))