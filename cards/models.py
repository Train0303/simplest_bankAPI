from django.db import models
from config.core.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from datetime import datetime
# Create your models here.

class Card(TimeStampedModel):
    account = models.ForeignKey('cards.Account',on_delete=models.CASCADE,related_name='account_card')
    cardNum = models.CharField(max_length=16, unique=True)
    pinNum = models.CharField(max_length=128) 
    year = models.IntegerField()
    month = models.IntegerField()
    
    @property
    def is_valid(self):
        now = datetime.now()
        year,month = now.year, now.month
        
        if year > 2000+self.year:
            return False
        elif year == self.year and month > self.month:
            return False
        return True
    
    def __str__(self):
        return f'{self.cardNum}/{self.account}'

class Account(TimeStampedModel):
    accountNum = models.CharField(max_length=20,unique=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.accountNum}'

class Transactions(TimeStampedModel):
    class TransactionMethod(models.TextChoices):
        DEPOSIT = 'DP', _('입금')
        WITHDRAW = 'WD' , _('출금')
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='card_transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_transactions')
    method = models.CharField(max_length=2, choices=TransactionMethod.choices)
    price = models.IntegerField()
    
    def __str__(self):
        return f'{self.method}/{{self.account}}/{self.price}'