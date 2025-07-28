from django.db import models

# Create your models here.
langChoices={
    'cpp':'cpp',
    'python':'python'
}


class Submission(models.Model):
    
    language=models.CharField()
    input=models.TextField()
    exp_result=models.TextField()
    output=models.TextField()
    status=models.CharField(max_length=1000,default='queued')
    src=models.TextField()
    time=models.FloatField(default=0)
    memory=models.IntegerField(default=0)
    #setLimit=models.CharField(default="no")
    timeLimit=models.FloatField(default=3)
    memLimit=models.IntegerField(default=256000)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table='Submission'

