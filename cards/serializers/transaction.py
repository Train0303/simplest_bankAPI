from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import check_password,make_password

from cards.models import Transactions

class TransactionsBaseSerializer(serializers.ModelSerializer):
    # 해당 방법으로 안해주면 card, account의 값이 pk값으로 나옴
    card = serializers.SlugRelatedField(
        slug_field='cardNum',
        read_only = True
    )
    account = serializers.SlugRelatedField(
        slug_field='accountNum',
        read_only = True
    )
    
    class Meta:
        model = Transactions
        fields = ('card','account','method','price',)
    

class TransactionSerializer(TransactionsBaseSerializer):
    balance = serializers.SerializerMethodField()

    class Meta(TransactionsBaseSerializer.Meta):
        fields = TransactionsBaseSerializer.Meta.fields + ('balance',)
        extra_kwagrs = {
            'method' : {'required':True},
            'price' : {'required':True},
        }
    
    def get_balance(self,obj):
        return self.context['balance']
    
    def validate_price(self,value):
        if value < 0:
            raise ValidationError({
                'price' : '가격은 양수만 입력 부탁드립니다.'
            })
        return value    
    
    def validate(self, data):
        method = data.get('method')
        price = data.get('price')
        
        #--------card validation---------
        card = self.context.get('card')
        if card is None:
            raise ValidationError({
                'card' : 'This field is required'
            })
        
        if not card.is_valid:
            raise ValidationError({
                'card' : '해당 카드는 유효기간이 지난 카드입니다.'
            })
        
        if not check_password(self.context['pinNum'], card.pinNum):
            raise ValidationError({
                'card' : '등록된 카드의 핀번호가 맞지 않습니다.'
            })
        
        #--------account validation---------
        account = self.context.get('account')
        if account is None:
            raise ValidationError({
                'account' : 'This field is required'
            })
        
        if (method == Transactions.TransactionMethod.WITHDRAW) and (account.balance - price < 0):
            raise ValidationError({
                'price' : '잔금을 초과하는 금액을 출금할 수 없습니다.'
            })
            
        return data

    def create(self, validated_data):
        method = validated_data.get('method')
        account = self.context.get('account')
        card = self.context.get('card')
        price = validated_data.get('price')
        
        if method == Transactions.TransactionMethod.WITHDRAW:
            account.balance -= price
        else:
            account.balance += price
        account.save()
        
        # validated_data에 데이터가 있어야 Meta에서 fields를 인식함
        # 만약 다른 방법을 사용하려면 serializerMethodField의 get_obj를 통해서 사용해야함.
        validated_data['account']= account
        validated_data['card'] = card
        Transactions.objects.create(**validated_data)
        self.context['balance'] = account.balance
        return validated_data