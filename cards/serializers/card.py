from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from cards.models import Card,Account

from datetime import datetime
import re

class CardBaseSerializer(serializers.ModelSerializer):
    # ModelSerializer를 그냥 Serializer로 고치면 Card에 대한 get 쿼리를 없앨 수 있지만 일관성을 위해 그냥 쿼리하나 정도는 줬다.
    class Meta:
        model = Card
        fields = ('cardNum','pinNum','year','month')
        extra_kwargs = {
            'pinNum' : {'write_only' : True}
        }
        

class CreateCardSerializer(CardBaseSerializer):
    accountNum = serializers.CharField(required=True)
    
    class Meta(CardBaseSerializer.Meta):
        fields = CardBaseSerializer.Meta.fields + ('accountNum',)
        extra_kwargs = {
            'pinNum' : {'write_only' : True, 'required' : True},
            'cardNum' : {'required' : True},
            'year' : {'required' : True},
            'month' : {'required' : True}
        }
    
    def validate_accountNum(self, value):
        try:
            account=Account.objects.get(accountNum = value)
        except Account.DoesNotExist:
            raise ValidationError({
                'accountNum' : "해당 게좌번호는 등록되지 않은 계좌번호입니다."
            })
        self.context['account'] = account
        return value
    
    # 해당 코드가 없어도 db에서 unique 특성에 의해 알아서 예외처리가 됨
    # def validate_cardNum(self, value):
    #     if Card.objects.filter(cardNum=value).exists():
    #         raise ValidationError({
    #             'cardNum' : '이미 등록된 카드번호입니다.'
    #         })
    #     return value
    
    def validate_year(self, value):
        if not re.fullmatch('[0-9]{2}',str(value)):
            raise ValidationError({
                'year' : '잘못된 년도 입력입니다.'
            })
        return value
    
    
    def validate_month(self, value):
        if not(1<=value<=12):
            raise ValidationError({
                'month' : '잘못된 월 입력입니다.'
            })
        return value
    
    def validate(self, data):
        year  = 2000+data.get('year')
        month = data.get('month')
        now = datetime.now()
       
        if year < now.year:
            raise ValidationError({
                'cardNum':'카드 유효기간이 지났습니다.'
                })
        elif year == now.year and month < now.month:
            raise ValidationError({
                'cardNum':'카드 유효기간이 지났습니다.'
                })
        
        if not(re.fullmatch('[0-9]{4}',data.get('pinNum'))):
            raise ValidationError({
                'pinNum':'유효하지 않은 pin번호를 입력하셨습니다.'
                })

        if not (re.fullmatch('[0-9]{16}',data.get('cardNum'))):
            raise ValidationError({
                'cardNum':'유효하지 않은 카드번호를 입력하셨습니다.'
                })
        
        return data

    def create(self, validated_data):
        encrypt_pinNum = make_password(validated_data['pinNum'])
        validated_data['pinNum'] = encrypt_pinNum
        account = self.context['account']
        Card.objects.create(
            account = account,
            cardNum = validated_data['cardNum'],
            pinNum = encrypt_pinNum,
            year = validated_data['year'],
            month = validated_data['month'],
        )
        
        return validated_data
    

class AccountBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('accountNum', 'balance',)

class CreateAccountSerializer(AccountBaseSerializer):
    
    class Meta(AccountBaseSerializer.Meta):
        read_only_fields = ('balance',)
        extra_kwargs ={
            'accountNum' : {'required':True},
        }
        
    def validate(self, data):
        accountNum = data.get('accountNum',None)
        
        if not(re.fullmatch('[0-9]{14}', accountNum)):
            raise ValidationError({
                'accountNum':'유효하지 않은 계좌번호를 입력하셨습니다.'
                })
        
        return data