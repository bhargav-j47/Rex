from rest_framework.response import Response
from rest_framework.views import APIView


class Submit(APIView):

    def post(self,request):
        return Response(request.data)



class Check(APIView):

    def get(self,request):
        
        _id=request.GET.get('id')

        return Response("hi you id is "+_id)