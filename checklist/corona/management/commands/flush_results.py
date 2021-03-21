from django.core.management.base import BaseCommand, CommandError
from corona.models import 문진결과
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Flushes Expired Results for all users'
    
    # flush by time : you can be moved to celery if in need
    # flush(id) eradicates all 문진결과 that is over 13 days old
    def handle(self, *args, **options):
        dayto = date.today()
        total = 문진결과.objects.filter(date  = date.today()- timedelta(days = 14))
        for result in total: result.delete()  
        self.stdout.write(self.style.SUCCESS('Sucessfully flushed results '))