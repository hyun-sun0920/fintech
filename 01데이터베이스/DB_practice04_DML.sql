use korea_stock_info;
show tables;
select * from stock_company_info;
select * from 2024_09_stock_price_info;

use korea_exchange_rate;
show tables;
select count(*) from exchange_rate;
select * from exchange_rate where date >= "2020-01-01" and date <= "2020-12-31" and 통화="유로 EUR";

# 2020년 1월1일부터 12월 31일까지 데이터에서 통화별 현찰살때 환율의 평균
select 통화, min(현찰_살때_환율) 최저가, max(현찰_살때_환율) 최고가, round(AVG(현찰_살때_환율), 2) 평균가 from exchange_rate 
where date >= "2020-01-01" and date <= "2020-12-31" group by 통화;

use korea_stock_info;
show tables;

#7, 8, 9월로 나눠져 있는 데이터를 1개의 테이블로 모으기 위해서는 join을 쓸 수 없으므로 union을 사용
create table stock_2024_alll AS
select * from 2024_07_stock_price_info
union all
select * from 2024_08_stock_price_info
union all
select * from 2024_09_stock_price_info;

###############################
#SQL 함수: SELECT 함수(값)
# 절대값 ABS()
Select abs(-34), abs(1), abs(-256);

#문자열 길이 측정: length(문자열);  공백도 문자임
select length("mysql database");

#반올림 함수 round()
select round(3.14567, 2);
select round(3.14467, 2);

#올림 ceil, 내림 floor
select ceil(4.5);
select ceil(4.1);
select floor(4.9);

#연산자를 통한 계산 +, -, *, /, %(나머지), div(몫만 반환), mod(나머지)
select 7/2;
select 7*2;
select 7+2;
select 7-2;
select 7 div 2;
select 7 mod 2;

#power(제곱), sqrt(루트), sign(음수, 양수 확인): 1이면 양수, -1이면 음수
select power(4, 3);
select sqrt(3);
select sign(5), sign(-78);

#truncate(값, 자릿수) 버림
select round(2.2345, 3), truncate(2.2345, 3);
select round(1153.2345, -2), truncate(1153.2345, -2);

select char_length('my sql'), length('my sql');
select char_length('홍 길동'), length('홍 길동'); #한글에서 length는 자음, 모음 하나씩 계산

#문자를 연결하는 함수 concat(), concat_ws()
select concat(' this', ' is ', 'mysql') as concat1; 
select concat_ws(' ', 'this', 'is', 'mysql') as concat3;
select concat_ws(' vs ', '헐크', '아이언맨', '타노스');

#대문자를 소문자로 lower(), 소문자를 대문자로 upper()
select lower('ABcd');
select upper('efgh');

#문자열의 자릿수를 일정하게 하고 빈 공간을 지정한 문자로 채우는 함수
#lpad(값, 자릿수, 채울문자), rpad(값, 자릿수, 채울문자)
select lpad('sql', 7, "#");
select lpad('sql', 7, " ");
select lpad('sql', 7, "=");
select rpad('sql', 7, "=");

#공백을 없애는 함수 ltrim(문자열), rtrim(문자열)
select ltrim('       sql        ');
select rtrim('       sql        ');

#문자열의 공백을 앞 뒤로 삭제하는 trim()
select trim('       sql         ');
select trim('      my sql         '); #문자열 사이의 공백은 못 없앰

#문자열을 잘라내는 함수 left(문자열, 길이), right(문자열, 길이)
select left('this is my sql', 4);
select right('this is my sql', 5);

select left('이것이 mysql이다.', 5);

# 문자열을 중간에서 잘라내는 함수 substr(문자열, 시작위치, 길이)
select substr('this is my sql', 6, 5);
select substr('this is my sql', 6);

#문자열의 공백을 앞 뒤로 삭제하고 문자열 앞 뒤에 포함된 특정 문자도 삭제하는 함수
#trim(leading '삭제할 문자' from 전체 문자열)
select trim('    my sql    ');
select trim(leading '*' from '****my sql****');
select trim(trailing '*' from '****my sql****');
select trim(both '*' from '****my sql****');

#날짜형 함수
select curdate(); #현재 년월일
select curtime(); #현재 시간
select now(); #현재 년원일 + 현재 시간
select current_timestamp(); #현재 년원일 + 현재 시간

#요일 표시 함수 dayname(날짜)
select dayname(now());
select dayname("2025-12-25");

#요일을 번호로 표시 dayofweek(날짜), 일(1), 월(2), 화(3)... 토(7)
select dayofweek(now());
select dayofweek("2024-05-05");

#1년 중 오늘이 몇일쨰인지 dayofyear(날짜)
select dayofyear(now());
select dayofyear("2025-05-08");

#날짜를 세분화 해서 보는 함수들
#현재 달의 마지막 날이 몇 일까지 있는지 출력
select last_day(now());
select last_day("2025-10-01");

#입력한 날짜에서 연도만 추출
select year(now());
select year("2025-10-01");

#입력한 날짜에서 월만 출력
select month(now());
select month("2025-10-01");
select monthname("2025-10-01");

#몇 분기인지 출력
select quarter(now());
select quarter("2025-12-13");

#몇 주차인지
select weekofyear(now());
select weekofyear("2025-12-25");

#날짜와 시간이 같이 있는 데이터에서 날짜와 시간을 구분해주는 함수
select now();
select date(now());

#날짜를 지정한 날 수 만큼 더하는 함수 
select date_add(now(), interval 5 day);
select adddate(now(), 5);

#날짜를 지정한 날 수 만큼 빼는 함수
select subdate(now(), interval 5 day);
select subdate(now(), 5);

#날짜와 시간을 년월, 날짜 시간, 분초 단위로 추출하는 함수
select extract(year_month from now());
select extract(day_hour from now());
select extract(minute_second from now());

#날짜 1에서 날짜 2를 뺀 일 수 계산
select datediff(now(), '2024-12-25');

#날짜 포멧 함수 - 지정한 형식에 맞춰서 출력해주는 함수
# %Y 4자리 연도, %y 2자리 연도
#%M 월의 영문표기, %m 2자리 월 표시, %b 월의 축약 영문표기 
#%d 2자리 일 표기, %e 1자리 일 표기
select date_format(now(), '%d-%b-%Y');
select date_format("2025-01-01", '%e-%M-%Y')

#시간 표기
# %H 24시간, %h 12시간, %p Am, Pm 표시 
# %i 2자리 분 표기
# %S 2자리 초
# %T 24시간 표기법 시:분:초
# %r 12시간 표기법 시:분: 초 AM/PM
# %W 요일의 영문표기, %w 숫자로 요일 표시 (일0, 월1, 화2, 수3, 목4, 금5, 토6)
select date_format(now(), '%H:%i:%S');
select date_format(now(), '%T');
select date_format(now(), '%r');