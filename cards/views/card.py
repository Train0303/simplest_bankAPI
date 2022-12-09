from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status

from cards.models import Card, Account
from cards.serializers.card import (CardBaseSerializer,
                                    CreateCardSerializer,
                                    CreateAccountSerializer,
                                    AccountBaseSerializer,
                                    )

from config.core.utils import query_profiler


class CreateCardView(APIView):
    @query_profiler
    def post(self,request):
        # 쿼리 3번 떄림
        serializer = CreateCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CreateAccountView(APIView):
    def post(self, request):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CardListView(ListAPIView):
    serializer_class = CardBaseSerializer
    
    def get_queryset(self):
        account_num = self.request.GET.get('accountNum')
        if account_num is not None:
            return Card.objects.filter(account__accountNum = account_num)
            
        return Card.objects.all()
    
    @query_profiler
    def list(self,request):
        quertset = self.get_queryset()
        serializer = self.serializer_class(instance=quertset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AccountListView(ListAPIView):
    queryset = Account.objects
    serializer_class = AccountBaseSerializer
    
    def get_queryset(self):
        account_num = self.request.GET.get('accountNum')
        if account_num is None:
            raise ValidationError({
                'accountNum' : '확인할 계좌번호를 입력해주세요.' 
            })
        
        try:
            account = self.queryset.get(accountNum=account_num)
        except Account.DoesNotExist:
            raise ValidationError({
                'accountNum' : '확인할 계좌번호가 존재하지 않습니다.' 
            })
            
        return account
    
    @query_profiler
    def list(self,request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(instance=queryset)
        
        return Response(serializer.data, status=status.HTTP_200_OK)