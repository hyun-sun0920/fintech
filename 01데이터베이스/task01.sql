use titanic;

#1. passenger, ticket, survived 테이블을 조인하고 Survived가 1인 사람들만 찾아서 Name, Age, Sex, Pclass, survived 컬럼을 출력하시오.
select Name, Age, Sex, Pclass, survived from passenger p inner join ticket t on p.PassengerId = t.PassengerId inner join survived s on p.PassengerId=s.PassengerId;


#2. 1의 결과를 10개만 출력하시오.
select Name, Age, Sex, Pclass, survived from passenger p inner join ticket t on p.passengerId = t.passengerId inner join survived s on p.passengerId=s.passengerId limit 10;

#3. Passenger 테이블을 기준 ticket, survived테이블을 LEFT JOIN 한 결과에서 성별이 여성이면서 Pclass가 1인 사람 중 생존자(survived=1)를 찾아 이름, 성별, Pclass를 표시하시오.(틀림)
select Name, Sex, Pclass from Passengger p left join ticket t on p.PassengerId = t.PassengerId left join survived s on p.PassengerId=s.PassengerId where Sex="female" and Pclass = 1;

#4. passenger, ticket, survived 테이블을 left join 후 나이가 10세 이상 20세 이하 이면서 Pclass 2인 사람 중 생존자를  표시하시오.
select survived from passenger p left join ticket t on p.passengerId = t.passengerId left join survived s on p.passengerId= s.passengerId where age between 10 and 20 and Pclass = 2;


#5. passenger, ticket, survived 테이블을 left join 후 성별이 여성 또는 Pclass 가 1인 사람 중 생존자를 표시하시오.(틀림)
select survived from passenger p left join ticket t on p.passengerId=t.passengerId left join survived s on p.passengerId=s.passengeId where Sex = "female" or Pclass = 1;

#6.  passenger, ticket, survived 테이블을 left join 후 생존자 중에서 이름에 Mrs가 포함된 사람을 찾아 이름, Pclass, 나이, Parch, Survived 를 표시하시오.
select Name, Pclass, Age, Parch, Survived from passenger p left join ticket t on p.passengerId = t.passengerId left join survived s on p.passengerId= s.passengerId where Name like "%MRS%";


#7. passenger, ticket, survived 테이블을 left join 후 Pclass가 1, 2이고 Embarked가 s, c 인 사람중에서 생존자를 찾아 이름, 성별, 나이를 표시하시오.
select Name, Sex, Age from passenger p left join ticket t on p.passengerId = t.passengerId left join survived s on p.passengerId = s.passengerId where Pclass in(1,2) and Embarked in("C","S");

#8. passenger, ticket, survived 테이블을 left join 후 이름에 James가 들어간 사람중 생존자를 찾아 이름, 성별, 나이 를 표시하고 나이를 기준으로 내림차순 정렬하시오.
select Name, Sex, Age from passenger p left join ticket t on p.passengerId=t.passengerId left join survived s on p.passengerId=s.passengerId order by Age desc;

#9. passenger, ticket, survived 테이블을 INNER JOIN한 데이터에서 성별별, 생존자의 숫자를 구하시오. 생존자 숫자 결과는 별칭을 Total로 하시오.
select count(survived) as Total from passenger p inner join ticket t on p.passengerId=t.passengerId inner join survived s on p.passengerId=s.passengerId group by Sex;

#10. passenger, ticket, survived 테이블을 INNER JOIN한 데이터에서 성별별, 생존자의 숫자, 생존자 나이의 평균을 구하시오. 생존자 숫자 결과는 별칭을 Total로 하시오.
select count(survived) as Total, AVG(Age) from passenger p inner join ticket t on p.passengerId=t.passengerId inner join survived s on p.passengerId=s.passengerId group by Sex;

#11. passenger, ticket, survived 테이블을 INNER JOIN한 데이터에서 성별별, pclass별, 생존자별로 pclass, sex, survived , survived의 클래스별 합계, 생존자/사망자의 나이 평균을 구하시오. 
#survived의 별칭은 is_survived로, 생존자 클래스별 합계는 별칭을 survived_total로, 생존자/사망자의 나이 평균은 별칭을 avg_age로 하시오.
select count(Pclass), count(sex), count(survived) as survived_total, AVG(Age) as avg_age from passenger p inner join ticket t on p.passengerId=t.passengerId inner join survived s on p.passengerId=s.passengerId group by Sex, Pclass, survived;