create table resident (
id integer primary key autoincrement,
name varchar(30) not null,
phoneNumber varchar(30) unique,
paypal varchar(50) null
);

create table bills (
id integer primary key autoincrement,
buyer_id integer not null references resident on delete set null,
amount float not null,
status varchar(10) not null default 'REGISTERED',
transaction_details varchar(64) null,
added timestamp default current_timestamp,
check(status = 'REGISTERED' and transaction_details is NULL or status = 'REPAID' or status = 'REFUNDED')
);;