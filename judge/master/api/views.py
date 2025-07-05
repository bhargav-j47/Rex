from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Submission
from .serializers import checkSerializer,submitSerializer

class Submit(APIView):

    def post(self,request):
        sdata=submitSerializer(data=request.data)
        if(sdata.is_valid()):
            obj=sdata.save()
            return Response({"id":obj.id ,'status':obj.status},status=201)

        return Response(sdata.errors,status=400)



class Check(APIView):

    def get(self,request):
        
        _id=request.GET.get('id')
        if(_id==None):
            return Response('id not provided',status=204)
        obj=Submission.objects.filter(id=_id)

        if(not obj):
           return Response("incorrect id",status=400)

        sres=checkSerializer(obj,many=True)
        return Response(sres.data,status=202)
        