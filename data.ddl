create table resident (
id integer primary key autoincrement,
name varchar(30) not null,
phoneNumber varchar(30) unique,
paypal varchar(50) null
);

create table bills (
id integer primary key autoincrement,
accounting_period integer references accounting_periods,
buyer_id integer not null references resident on delete set null,
amount float not null,
status varchar(10) not null default 'REGISTERED',
added timestamp default current_timestamp,
check(status = 'REGISTERED' or status = 'PROCESSED')
);

create table payments (
    id integer primary key autoincrement,
    resident_id references resident on delete set null,
    accounting_period integer references accounting_periods,
    amount float not null,
    status varchar(10) not null default 'PENDING',
    transaction_details varchar(64) null,
    check(status = 'PENDING' or status = 'PAID')
);

create table accounting_periods (
    number integer primary key,
    start timestamp default current_timestamp,
    end timestamp null
);

insert into accounting_periods(number) VALUES(1);