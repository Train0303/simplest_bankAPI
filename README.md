# simplest_bankAPI
Django Rest Framework를 연습하기 위한 간단한 CRUD API서버

---
### 구현 목록
1. 계좌 등록
2. 카드 등록
3. 입금
4. 출금
5. 거래 내역
6. 계좌와 연동된 카드 목록
7. 계좌 조회
---
### 실행 및 테스트
실행 및 테스트를 위해서는 다음과 같은 명령어를 실행시키면 됩니다.
```
python manage.py makemirations
python manage.py migrate
python manage.py runserver
python manage.py test
```
---
### 추가사항
- 쿼리 최적화를 위해 View별 쿼리를 출력하는 데코레이터 query_profiler 추가했습니다.
- 쿼리 수를 최대한으로 낮추도록 노력했습니다.
- View에서 처리하는 Validation을 최대한 Serializer로 이식했습니다.
- 동시성 문제를 고려하여 select_for_update를 통한 테이블 row lock을 추가했습니다. 