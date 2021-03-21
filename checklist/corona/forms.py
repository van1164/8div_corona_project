from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class EditSurveyForm(forms.Form):
    Q1 = forms.CharField(help_text = "1번 질문 입력:", max_length = 200, required = True)
    Q2 = forms.CharField(help_text = "2번 질문 입력:", max_length = 200, required = True)
    Q3 = forms.CharField(help_text = "3번 질문 입력:", max_length = 200, required = True)
    Q4 = forms.CharField(help_text = "4번 질문 입력:", max_length = 200, required = True)
    Q5 = forms.CharField(help_text = "5번 질문 입력:", max_length = 200, required = True)
    Q6 = forms.CharField(help_text = "6번 질문 입력:", max_length = 200, required = True)
    Q7 = forms.CharField(help_text = "7번 질문 입력:", max_length = 200, required = True)
    Q8 = forms.CharField(help_text = "8번 질문 입력:", max_length = 200, required = True)
    Q9 = forms.CharField(help_text = "9번 질문 입력:", max_length = 200, required = True)
    Q10 = forms.CharField(help_text = "10번 질문 입력:", max_length = 200, required = True)

        





