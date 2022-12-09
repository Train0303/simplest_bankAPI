from django.contrib import admin
from .models import Card,Account,Transactions
from typing import Sequence
# Register your models here.


class CardAdmin(admin.ModelAdmin):
    search_fields: Sequence[str] = ('cardNum',)
    list_display = ('cardNum','pinNum','year','month','account', )
    
    
class AccountAdmin(admin.ModelAdmin):
    search_fields: Sequence[str] = ('accountNum',)
    list_display = ('accountNum','balance',)

class TransactionAdmin(admin.ModelAdmin):
    search_fields: Sequence[str] = ('card__cardNum',)
    list_display = ('card', 'account','method','price', )

admin.site.register(Card,CardAdmin)
admin.site.register(Account,AccountAdmin)
admin.site.register(Transactions,TransactionAdmin)