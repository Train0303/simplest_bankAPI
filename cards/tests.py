# from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time as 오늘_날짜_고정
from rest_framework.test import APIClient
from rest_framework.response import Response
from test_plus import TestCase
# Create your tests here.

class CardTestCase(TestCase):
    client_class = APIClient
    
    def do_계좌_등록(self,account_id:str)->Response:
        res:Response = self.client.post(
            reverse('cards:account_create'),
            data={
                'accountNum':account_id
            },
            format='json'
        )
        return res
        
    def do_카드_등록(self,**kwargs)->Response:
        account_id = kwargs.get('account_id')
        pin_num = kwargs.get('pin_num')
        card_id = kwargs.get('card_id')
        card_year = kwargs.get('card_year')
        card_month = kwargs.get('card_month')
        
        res:Response = self.client.post(
            reverse('cards:card_create'),
            data={
                'accountNum' : account_id,
                'cardNum' : card_id,
                'pinNum' : pin_num,
                'year' : card_year,
                'month' : card_month 
            },
            format='json'
        )
        
        return res
    
    def do_계좌_입금(self,pin_num = None, card_num = None, price=None)->Response:
        res:Response = self.client.post(
            reverse('cards:deposit'),
            data={
                'pinNum' : pin_num,
                'cardNum' : card_num,
                'price' : price
            }
        )
        return res
    
    def do_계좌_출금(self, pin_num = None, card_num = None, price=None)->Response:
        res:Response = self.client.post(
            reverse('cards:withdraw'),
            data = {
                'pinNum' : pin_num,
                'cardNum' : card_num,
                'price' : price
            }
        )
        return res
    
    def do_계좌_확인(self, account_num)->Response:
        res:Response = self.client.get(
            reverse('cards:account_list'),
            data={
                'accountNum' : account_num
            }
        )
        return res
    
    def do_계좌로_된_카드_확인(self, account_num=None)->Response:
        res:Response = self.client.get(
            reverse('cards:card_list'),
            data = {
                'accountNum' : account_num
            }
        )
        return res
    
    def do_거래내역_확인(self, account_num=None, card_num=None) ->Response:
        res:Response = self.client.get(
            reverse('cards:transaction_list'),
            data = {
                'accountNum' : account_num,
                'cardNum' : card_num
            }
        )
        return res
    
    def test_게좌_등록_실패_정보부족(self):
        res = self.client.post(reverse('cards:account_create'))
        self.assertEqual(res.status_code, 400)
    
    def test_계좌_등록_과_중복검사(self):
        account_id:str = '11012341234568'
        
        res = self.do_계좌_등록(account_id=account_id)
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_id)
        self.assertEqual(res.data['balance'], 0)
        
        res = self.do_계좌_등록(account_id=account_id)
        self.assertEqual(res.status_code,400)
    
    def test_계좌_등록_유효_체크(self):
        # 14자리가 아닌 13자리
        account_num:id = '1101234123456'
        res = self.do_계좌_등록(account_id=account_num)
        self.assertEqual(res.status_code, 400)
    
    def test_카드_등록_실패_정보부족(self):
        # 카드 정보 부족
        res = self.client.post(reverse('cards:card_create'))
        self.assertEqual(res.status_code, 400)
        
    def test_카드_등록_실패_유효기간_지남(self):
        card_id = '1111222233334444'
        card_year = 21
        card_month = 5
        pin_num = '0303'
        account_id:str = '11012341234568'
        
        # 카드 유효기간 지남
        with 오늘_날짜_고정('2022-07-01'):
            self.do_계좌_등록(account_id=account_id)
            
            res = self.do_카드_등록(**{
                    'card_id': card_id,
                    'pin_num' : pin_num,
                    'account_id' : account_id,
                    'card_year' : card_year,
                    'card_month' : card_month
                })
            self.assertEqual(res.status_code, 400)
            
    def test_카드_등록_성공(self):
        card_id = '1111222233334444'
        card_year = 23
        card_month = 5
        pin_num = '0303'
        account_id:str = '11012341234568'
        
        with 오늘_날짜_고정('2022-07-01'):
            self.do_계좌_등록(account_id=account_id)
            res = self.do_카드_등록(**{
                    'card_id': card_id,
                    'pin_num' : pin_num,
                    'account_id' : account_id,
                    'card_year' : card_year,
                    'card_month' : card_month
            })
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_id)
            self.assertEqual(res.data['cardNum'],card_id)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
        

    def test_계좌_입금_실패_정보부족(self):
        res = self.client.post(
            reverse('cards:deposit')
        )    
        self.assertEqual(res.status_code, 400)
        
    def test_계좌_입금_실패_카드번호틀림(self):
        account_num = '11012341234568'
        card_num = '1111222233334444'
        pin_num = '0303'
        card_year = 23
        card_month = 6
        
        res = self.do_계좌_등록("11012341234568")
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_num)
        self.assertEqual(res.data['balance'], 0)
        
        with 오늘_날짜_고정('2022-12-09'):
            res = self.do_카드_등록(card_id=card_num,account_id=account_num,pin_num=pin_num,card_year=23,card_month=6)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_num)
            self.assertEqual(res.data['cardNum'],card_num)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
            
            res = self.do_계좌_입금(card_num=card_num, pin_num='0304',price=10000)
            self.assertEqual(res.status_code, 400)
        
    
    def test_계좌_입금_성공(self):
        account_num = '11012341234568'
        card_num = '1111222233334444'
        pin_num = '0303'
        card_year = 23
        card_month = 6
        price = 10000
        
        res = self.do_계좌_등록("11012341234568")
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_num)
        self.assertEqual(res.data['balance'], 0)
        
        with 오늘_날짜_고정('2022-12-09'):
            res = self.do_카드_등록(card_id=card_num,account_id=account_num,pin_num=pin_num,card_year=23,card_month=6)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_num)
            self.assertEqual(res.data['cardNum'],card_num)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
            
            res = self.do_계좌_입금(card_num=card_num, pin_num=pin_num,price=price)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['card'],card_num)
            self.assertEqual(res.data['account'],account_num)
            self.assertEqual(res.data['method'],'DP')
            self.assertEqual(res.data['price'],price)
            self.assertEqual(res.data['balance'],10000)
    
    def test_계좌_출금_실패_정보부족(self):
        res = self.client.post(
            reverse('cards:withdraw')
        )    
        self.assertEqual(res.status_code, 400)
        
    def test_계좌_출금_실패_카드번호틀림(self):
        account_num = '11012341234568'
        card_num = '1111222233334444'
        pin_num = '0303'
        card_year = 23
        card_month = 6
        
        res = self.do_계좌_등록("11012341234568")
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_num)
        self.assertEqual(res.data['balance'], 0)
        
        with 오늘_날짜_고정('2022-12-09'):
            res = self.do_카드_등록(card_id=card_num,account_id=account_num,pin_num=pin_num,card_year=23,card_month=6)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_num)
            self.assertEqual(res.data['cardNum'],card_num)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
            
            res = self.do_계좌_입금(card_num=card_num, pin_num=pin_num,price=10000)
            self.assertEqual(res.status_code, 201)
            
            res = self.do_계좌_출금(card_num=card_num,pin_num='0304',price=5000)
            self.assertEqual(res.status_code, 400)
            
    def test_계좌_출금_실패_잔액부족(self):
        account_num = '11012341234568'
        card_num = '1111222233334444'
        pin_num = '0303'
        card_year = 23
        card_month = 6
        
        res = self.do_계좌_등록("11012341234568")
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_num)
        self.assertEqual(res.data['balance'], 0)
        
        with 오늘_날짜_고정('2022-12-09'):
            res = self.do_카드_등록(card_id=card_num,account_id=account_num,pin_num=pin_num,card_year=23,card_month=6)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_num)
            self.assertEqual(res.data['cardNum'],card_num)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
            
            res = self.do_계좌_입금(card_num=card_num, pin_num=pin_num,price=10000)
            self.assertEqual(res.status_code, 201)
            
            res = self.do_계좌_출금(card_num=card_num,pin_num=pin_num,price=15000)
            self.assertEqual(res.status_code, 400)
    
    def test_계좌_출금_성공(self) -> dict:
        account_num = '11012341234568'
        card_num = '1111222233334444'
        pin_num = '0303'
        card_year = 23
        card_month = 6
        in_price = 10000
        out_price = 5000
        
        res = self.do_계좌_등록(account_num)
        self.assertEqual(res.status_code,201)
        self.assertEqual(res.data['accountNum'], account_num)
        self.assertEqual(res.data['balance'], 0)
        
        with 오늘_날짜_고정('2022-12-09'):
            res = self.do_카드_등록(card_id=card_num,account_id=account_num,pin_num=pin_num,card_year=23,card_month=6)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['accountNum'],account_num)
            self.assertEqual(res.data['cardNum'],card_num)
            self.assertEqual(res.data['year'],card_year)
            self.assertEqual(res.data['month'],card_month)
            
            res = self.do_계좌_입금(card_num=card_num, pin_num=pin_num,price=in_price)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['card'],card_num)
            self.assertEqual(res.data['account'],account_num)
            self.assertEqual(res.data['method'],'DP')
            self.assertEqual(res.data['price'],in_price)
            self.assertEqual(res.data['balance'],10000)
            
            res = self.do_계좌_출금(card_num=card_num,pin_num=pin_num,price=out_price)
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data['card'],card_num)
            self.assertEqual(res.data['account'],account_num)
            self.assertEqual(res.data['method'],'WD')
            self.assertEqual(res.data['price'],out_price)
            self.assertEqual(res.data['balance'],in_price-out_price)
            
        return res.data
    
    def test_거래내역_확인(self):
        data = self.test_계좌_출금_성공()
        res:Response = self.client.get(
            reverse('cards:transaction_list'),
            data = {
                'cardNum' : data['card'],
                'accountNum' : data['account']
            }
        )
        self.assertEqual(res.status_code, 200)
    
    def test_카드_확인(self):
        res:Response = self.client.get(
            reverse('cards:card_list'),
        )
        self.assertEqual(res.status_code, 200)
    
    def test_계좌_확인(self):
        account_num = '11012341234568'
        self.do_계좌_등록(account_id=account_num)
        
        res:Response = self.client.get(
            reverse('cards:account_list'),
            data = {
                'accountNum' : account_num
            }
        )
        self.assertEqual(res.status_code, 200)