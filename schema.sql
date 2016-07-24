drop table if exists entries;
drop table if exists users;
create table entries (
    id integer primary key autoincrement,
    title text not null,
    ip text not null,
    secret text not null
);

create table users (
    id integer primary key autoincrement,
    username text not null,
    password text not null
);

insert into users (username, password) values ("admin","default");

