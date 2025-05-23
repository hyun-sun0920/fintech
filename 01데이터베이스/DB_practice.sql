#view: select로 조회한 내용을 테이블을 만드는 것처럼 저장하는 것. 읽기 전용
# create view 뷰이름 as select문 
# drop view 뷰이름 

use korea_exchange_rate;
select * from exchange_rate;

# 1997년 1월 1일부터 2001년 12월 31일까지 환율변동 조회
select * from exchange_rate where date between "1997-01-01" and "2001-12-31";

#통화별로 현찰_살때_환율, 현찰_팔때_환율의 
# min() 살 때 최저환율, max() 살 때 최고환율, avg() 살 때 평균환율
# max() - min() 살 때 환율변동량
# max() - min() 팔 때 환율변동량
# min() 팔 때 최저환율, max() 팔 때 최고환율, avg() 팔 때 평균환율
# max() - min() 팔 때 환율변동량

create view exchange_rate_1997_2001 as 
select 통화, min(현찰_살때_환율) 살때최저환율, max(현찰_살때_환율) 살때최고환율, 
avg(현찰_살때_환율) 살때평균환율, max(현찰_살때_환율) - min(현찰_살때_환율) 살때환율변동량, 
min(현찰_팔때_환율) 팔때최저환율, max(현찰_팔때_환율) 팔때최고환율, avg(현찰_팔때_환율) 팔때평균환율,
max(현찰_팔때_환율) - min(현찰_팔때_환율) 팔때환율변동량 
from exchange_rate where date between "1997-01-01" and "2001-12-31"
group by 통화;

select * from exchange_rate_1997_2001 where 통화='미국 USD';




