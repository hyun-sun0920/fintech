USE titanic;
SHOW tables;
SELECT * FROM p_info;
SELECT Name From p_info;
select Name, Age from p_info;
desc p_info;
select * from p_info limit 10;
# 조건에 맞는 데이터 검색하기 - 성별이 남자인 경우만 조회하고 싶을 때
select * from p_info where Sex="male";

# 조건에 맞는 데이터 검색하기 - 나이가 40세 이상인 사람만 조회
select * from p_info where Age>=40;

# 조건을 2개 이상 줄 때: and, or - 성별이 남성이거나 나이가 10세 미만인 사람 조회
select * from p_info where Sex="male" or Age < 10;

select * from p_info where Sex="female" and 20<=Age<50;
select * from p_info where SibSp>=1 and Parch>=1;
select * from t_info where Pclass=1;
select * from t_info where Pclass=2 or Fare>50;
select * from survived where Survived=1;
desc t_info;
select * from t_info where Pclass=1;
select * from t_info where Pclass=2 or Fare > 50;
select * from survived where Survived=1;
select * from p_info where Sibsp in(1,2,3);

#like-문자열 안에서 특정 단어를 포함한 행을 찾을 때
SELECT * FROM p_info Where Name like "Rice%";
select * from p_info where name like "%Eric";



# in, like, between, is null, is not null
select * from p_info where Sibsp not in(0,1,2,3);

#between a and begin
select * from p_info where Age between 20 and 40;

#is null, is not null
select * from p_info where Age is null;
select * from p_info where Age is not null;

select * from t_info where Fare between 100 and 1000;
select * from t_info where Ticket like "pc%" and Embarked in("C","S");
select * from t_info where Pclass in(1,2);
select * from t_info where Cabin LIKE "%59%";


select * from p_info where Age is not null and Name like('%James%') and Age >= 40 and Sex="male";

#order by/group by로 데이터 순서 정렬하기 
# select * from 테이블명  where 컬럼명 + 조건 order by 기준컬럼
# asc는 오름차순 desc는 내림차순
select * from p_info where Age is not null and Name like "%Miss%" and Age<=40 and Sex="female" order by Age desc;

#group by 특정 컬럼을 기준으로 그룹 연산을 할 때 (평균, 최소값, 최대값, 행 개수)
select * from p_info Age is not null 

#avg-평균, min-최솟값, max-최대값, count() 행 개수 셀 때

select Sex, AVG(Age) from p_info where Age is not null group by Sex;

#having:그룹 연산 후의 결과에서 특정 조건을 충족하는 행을 찾고 싶을 때. group by 일 때는 having을 씀
select Pclass, AVG(Fare) from t_info group by Pclass order by Pclass having AVG(FARE) > 50;

#inner join: 왼쪽, 오른쪽에 있는 테이블에서 기준 컬럼의 값이 일치하는 것만 합침
select * from passenger limit 3;
select * from ticket limit 3;

select * from passenger inner join ticket on passenger.PassengerId = ticket. PassengerId;

#left join
select * from passenger LEFT JOIN ticket on passenger.passengerID = ticket.passengerId;
select * from passenger right JOIN ticket on passenger.passengerID = ticket.passengerId;

#두 개의 테이블을 조인하면서 Name, Age, Pclass, Fare만 보고 싶을 때
Select ticket.passengerId, Name, Age, Pclass, Fare From passenger inner join ticket on passenger.PassengerId = ticket. PassengerId;

#as: 약칭, 별칭

#as 생략하고 별칭
select p.passengerId, Name, Age, Pclss, Fare from passenger p left join ticket as t on p.PassengerId = t.PassengerId

#3개의 테이블을 1개로 합치기 (테이블 1 + 테이블 2) + 테이블 3
select * from passenger p inner join ticket t on p.PassengerId = t.PassengerId inner join survived s on p.PassengerId = s.PassengerId
