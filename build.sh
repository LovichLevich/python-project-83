#!/usr/bin/env bash
dropdb --if-exists mydb
createdb mydb
make install && psql -a -d $DATABASE_URL -f database.sql

