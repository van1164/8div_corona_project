from django.contrib import admin

# Register your models here.
from .models import 사단
from .models import 여단
from .models import 대대
from .models import 관리자
from .models import 간부
from .models import 질문지
from .models import 문진결과
from .models import 제출여부

admin.site.register(사단)
admin.site.register(여단)
admin.site.register(대대)
admin.site.register(관리자)
admin.site.register(간부)
admin.site.register(질문지)
admin.site.register(문진결과)
admin.site.register(제출여부)