#데이터베이스, 테이블 만들기
create database sampleDB;
Drop database sampleDB;

#데이터베이스 조회하기
#SHOW databases;

#테이블 만들기 create table 테이블명 (컬럼명1(데이터타입), 컬럼명2(데이터타입)....);
use sampledb;
create table customers(id int, name varchar(100), sex varchar(20), phone varchar(20), address varchar(255));

#테이블 삭제하기
drop table customers;

#market_db 만들기
create database market_db;
use market_db;

#hongong1 테이블 만들기 toy_id(int), toy_name(char(4)), age(int)
create table hongong1 (toy_id int, toy_name char(4), age int);
show tables;
desc hongong1;

#생성한 테이블에 데이터 입력하기 insert into 테이블명(컬럼명1, 컬럼명2, ) values (1, '우디', 25)
insert into hongong1(toy_id, toy_name, age) values(1, '우디', 25);
select * from hongong1;

insert into hongong1(toy_id, toy_name) values(2, '버즈');
insert into hongong1(toy_name, age, toy_id) values('제시', 20, 3);
insert into hongong1 values(5, '포테이토', 40)

#primary key와 auto increment 기능을 추가한 테이블 만들기
USE sample_db;
create table hongong2 (toy_id int AUTO_INCREMENT PRIMARY KEY, toy_name char(4), age int);

#auto increment가 지정된 테이블에 데이터 넣기
insert into hongong2 values (NULL, '보핍', 25);
insert into hongong2 values(NULL, '렉스', 21);
select * from hongong2;

#테이블 수정하기 alter
#컬럼 추가 alter table 테이블명 add column 컬럼명, 자료형, 속성(NOT NULL)
ALTER TABLE hongong2 add column country varchar(100);
select * from hongong2;

#기존 테이블에 있는 자료 update 하기 where와 함께: update 테이블명 set 컬럼명 = 업데이트 할 값 where toy_id=1;
update hongong2 set country='미국' where toy_id=1;

#테이블 내용은 모두 지우고 테이블의 구조는 남기고 싶을 때 truncate
TRUNCATE table hongong2;
select * from hongong2;

#테이블의 데이터 삭제 delete from 테이블명 where 조건
delete from hongong1 where toy_id=2;

# idx 컬럼추가 primary key로 지정 auto_increment
alter table hongong1 add column idx int primary key auto_increment;
delete from hongong1 where toy_id=2;

insert into hongong1 values(7, '렉스', 30, NULL);

#create, insert, update, delete, select

use sampledb;
create table member(id int auto_increment primary key, member_id varchar(6), name varchar(5), address varchar(25));
insert into member values(NULL, 'tess', '나훈아', '경기 부천시 중동');
insert into member values(NULL, "hero", "임영웅", "서울 은평구 증산동");
insert into member values(NULL, "iyou", "아이유", "인천 남구 주안동");
insert into member values(NULL, "tess", "나훈아", "경기 부천시 중동");
select * from member;

use market_db;
create table product(제품이름 varchar(15), 가격 int, 제조일자 varchar(30), 제조회사 varchar(20), 남은수량 int);
insert into product values('바나나', 1500, '2024-07-01', '델몬트', 17);
insert into product values('카스', 2500, '2023-12-12', 'OB', 3);
insert into product values('삼각김밥', 1000, '2025-02-26', 'CJ', 22);
select * from product;

# product 테이블에 prod_id 컬럼을 추가하고 auto_increment, primary key를 추가하기
use market_db;
alter table product add column prod_id int auto_increment primary key;
select * from product;

insert into member values(null, 'akmu', null);

#Rollback 연습
create database mywork;
create table emp_test(emp_no int not null, emp_name varchar(30) not null, hire_date date null, salary int null, primary key(emp_no));
desc emp_test;
insert into emp_test(emp_no, emp_name, hire_date, salary) values(1005, '쿼리', '2021-03-01', 4000),
(1006,'호킹','2021-03-05', 5000), (1007, '패러데이', '2021-04-01', 2200), (1008, '맥스웰', '2021-04-04', 3300),
(1009, '플랑크', '2021-04-05', 4400);
select * from emp_test;

#update 연습
#호킹의 salary를 10000으로 변경
update emp_test set salary=10000 where emp_no=1006;

#패러데이의 hire_date를 2023-07-11로 변경 
update emp_test set hire_date='2023-07-11' where emp_no=1007;

#플랑크가 있는 데이터를 삭제
delete from emp_test where emp_no=1009;

select * from emp_test;

#오토커밋 옵션 활성화: 결과가 1이면 오토커밋 활성화 0이면 비활성화 된 것
select @@autocommit;
set autocommit = 0; #오토커밋 비활성화
select @@autocommit;





















    
    
    
