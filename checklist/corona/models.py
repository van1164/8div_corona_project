from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date
# Create your models here.
class 대대(models.Model):
    name = models.CharField(max_length = 20, default = "무효")
    brigade = models.ForeignKey('여단', on_delete = models.PROTECT)

    def __str__(self):
        return str(self.id) + '. ' +self.name

class 간부(models.Model):
    user = models.OneToOneField(User)
    battalion = models.ForeignKey('대대', on_delete = models.PROTECT)

    def __str__(self):
        return str(self.id)+". "+self.username

class 여단(models.Model):
    name = models.CharField(max_length = 20, default = "무효")
    division = models.ForeignKey('사단', on_delete = models.PROTECT)

    def __str__(self):
        return str(self.id) + '. ' + self.name

class 사단(models.Model):
    name = models.CharField(max_length=15, default = "무효")

    def __str__(self):
        return str(self.id) + '. '+ self.name

class 관리자(models.Model):
    user = models.OneToOneField(User)
    access_levels = (
        ('Di', '사단장급'), # Division
        ('Br', '여단장급'), # Brigade
        ('Ba', '대대장급') # Battalion
    )
    access_level = models.CharField(
        max_length = 2,
        choices = access_levels,
        default = 'No',
        help_text = '접근권한'
    )
    adminofbatta = models.OneToOneField(
        '대대',
        on_delete = models.PROTECT,
        null=True,
        blank = True
    )
    adminofbrig = models.OneToOneField(
        '여단',
        on_delete = models.PROTECT,
        null=True,
        blank = True
    )
    adminofdiv = models.OneToOneField(
        '사단',
        on_delete = models.PROTECT,
        null=True,
        blank = True
    )

    def __str__(self):
        return str(self.username)

#< +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ >
class 제출여부(models.Model):
    brigade = models.ForeignKey(여단, on_delete = models.CASCADE, blank = True, null = True)
    battalion = models.ForeignKey(대대, on_delete = models.CASCADE, blank = True, null = True)
    date = models.DateField(auto_now_add = True)
    
    def __str__(self):
        if self.brigade == None:
            return str(self.battalion.name) + '의 ' + str(self.date) + ' 설문지'    
        else:
            return str(self.brigade.name) + '의 ' + str(self.date) + ' 설문지'
    
    def battalion_get_stats(self):
        num_house = len(문진결과.objects.filter(battalion = self.battalion).filter(date = date.today()).filter(is_fine = False))
        num_all = len(간부.objects.filter(battalion = self.battalion))
        num_rest = num_all - num_house
        return {'num_house' : num_house, 'num_rest' : num_rest}
    
    def brigade_get_stats(self):
        num_house = num_all = num_rest = 0
        battalions = 대대.objects.filter(brigade = self.brigade)
        for battalion in battalions:
            num_house += len(문진결과.objects.filter(battalion = battalion).filter(date = date.today()).filter(is_fine = False))
            num_all += len(간부.objects.filter(battalion = battalion))
        num_rest = num_all - num_house
        return {'num_house' : num_house, 'num_rest' : num_rest}
        
class 질문지(models.Model):
    ownership = models.OneToOneField(
        대대,
        on_delete=models.CASCADE,
    )
    last_revised = models.DateField(auto_now_add = True)
    Q1 = models.CharField(max_length=200)
    Q2 = models.CharField(max_length=200)
    Q3 = models.CharField(max_length=200)
    Q4 = models.CharField(max_length=200)
    Q5 = models.CharField(max_length=200)
    Q6 = models.CharField(max_length=200)
    Q7 = models.CharField(max_length=200)
    Q8 = models.CharField(max_length=200)
    Q9 = models.CharField(max_length=200)
    Q10 = models.CharField(max_length=200)

    def __str__(self):
        return str(self.ownership.name) + ' ' +str(self.last_revised) + '에 수정된 설문지'

    def get_all_qs(self):
        return [self.Q1,self.Q2,self.Q3,self.Q4,self.Q5,self.Q6,self.Q7,self.Q8,self.Q9, self.Q10]
    
    def get_dict_all_qs(self):
        return {
            'Q1':self.Q1,
            'Q2':self.Q2,
            'Q3':self.Q3,
            'Q4':self.Q4,
            'Q5':self.Q5,
            'Q6':self.Q6,
            'Q7':self.Q7,
            'Q8':self.Q8,
            'Q9':self.Q9,
            'Q10':self.Q10
        }

class 문진결과(models.Model):
    owner = models.ForeignKey(간부, on_delete = models.CASCADE)
    battalion = models.ForeignKey(대대, on_delete = models.PROTECT)
    questionnaire = models.ForeignKey(질문지, on_delete = models.PROTECT)
    date = models.DateField(auto_now_add = False)
    A1 = models.BooleanField()
    A2 = models.BooleanField()
    A3 = models.BooleanField()
    A4 = models.BooleanField()
    A5 = models.BooleanField()
    A6 = models.BooleanField()
    A7 = models.BooleanField()
    A8 = models.BooleanField()
    A9 = models.BooleanField()
    A10 = models.BooleanField()
    is_fine = models.BooleanField()
    
    def __str__(self):
        return str(self.owner.username) + '의 ' + str(self.date) + ' 설문지'

    def get_problematic_qs(self):
        result_lst = []
        ans_lst = self.get_all_as()
        q_lst = 질문지.objects.get(ownership = self.battalion).get_all_qs()
        for i in range(10):
            if ans_lst[i]: result_lst.append(i+1)
        return result_lst

    def get_all_as(self):
        return [self.A1,self.A2,self.A3,self.A4,self.A5,self.A6,self.A7,self.A8,self.A9, self.A10]

    def get_true_a_idx(self):
        lst = self.get_all_as()
        if self.is_fine: return []
        num_lst = []
        for i in range(10):
            if lst[i]: num_lst.append(i+1)
        return num_lst