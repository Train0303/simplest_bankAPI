from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework import status,generics

from django.db import transaction
from django.db.models import Q

from cards.models import Card, Account, Transactions
from cards.serializers.transaction import TransactionSerializer,TransactionsBaseSerializer
from config.core.utils import query_profiler

class TransactionAPIView(APIView):
    method = None
    
    # db 최적화 완료
    @query_profiler
    def post(self, request):
        if (pinNum:=request.data.get('pinNum',None)) is None:
            raise ValidationError({
                'pinNum' : '핀번호는 반드시 입력해야합니다.'
            })
        
        cardNum = request.data.get('cardNum')
        
        with transaction.atomic():
            try:
                card = Card.objects.select_related('account')\
                                    .select_for_update(nowait=False, of=('account'))\
                                    .get(cardNum = cardNum)
            except Card.DoesNotExist:
                raise ValidationError({
                    'cardNum' : "해당 카드번호가 존재하지 않습니다."
                })
            
            
            # pk를 그대로 넣어주게 되면 serializer에서 자체로 쿼리를 추가로 만들어서 데이터를 가져온다.
            serializer_data = {
                'method' : self.method,
                'price' : request.data.get('price'),
            }

            # 그렇기에 모델 데이터를 context로 넣어 처리해주면 추가적인 쿼리를 사용할 필요없이 데이터를 넣을 수 있다.
            serializer_context = {
                'pinNum' : pinNum,
                'card' : card,
                'account' : card.account
            }
            
            serializer = TransactionSerializer(data=serializer_data, context=serializer_context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class DepositAPIView(TransactionAPIView):
    method = Transactions.TransactionMethod.DEPOSIT
    
class WithdrawAPIView(TransactionAPIView):
    method = Transactions.TransactionMethod.WITHDRAW
    
class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionsBaseSerializer
    queryset = Transactions.objects
    
    def get_queryset(self):
        accountNum = self.request.GET.get('accountNum')
        cardNum = self.request.GET.get('cardNum')
        count = 0
        q = Q()
        if accountNum is not None:
            q &= Q(account__accountNum=accountNum)
        else:
            count+=1
        
        if cardNum is not None:
            q &= Q(card__cardNum=cardNum)
        else:
            count+=1
        
        if count == 2:
            raise ValidationError({
                'inputError' : '계좌번호, 카드번호 중 하나는 입력해야합니다.'
            })
            
        # n+1발생 -> 쿼리 최적화 완료
        return self.queryset.select_related('card','account').filter(q)
    
    
    @query_profiler
    def list(self,request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(instance=queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)