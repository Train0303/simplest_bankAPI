from typing import Callable

from django.conf import settings
from django.test.utils import CaptureQueriesContext
from django.db import connection

DEBUG = getattr(settings,'DEBUG',True)

# DEBUG가 True일 때, 쿼리를 추출해주는 코드
def query_profiler(func:Callable) -> Callable:
    def wrapper(*args, **kwargs):
        if DEBUG:
            f = open('./logs/sqltest.txt','w')
            f.write('\n')
            f.write(f"===== {func.__name__} called query check =====")
            with CaptureQueriesContext(connection) as context:
                target_func = func(*args, **kwargs)
                
                for index, query in enumerate(context.captured_queries):
                    sql = query.get('sql')
                    time = query.get('time')
                    
                    f.write(f'CALLED QUERY :: [{index}]')

                    f.write(f'CALLED QUERY :: query: {sql}')
                    f.write(f'CALLED QUERY :: executed time: {time}')
                    f.write("=====")
                    f.write('\n')
                f.close()
                return target_func
            
        target_func = func(*args, **kwargs)    
        return target_func
    
    return wrapper