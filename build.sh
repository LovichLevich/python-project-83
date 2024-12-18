#!/usr/bin/env bash
export $(grep -v '^#' .env | xargs)
make install && psql -a -d "$DATABASE_URL" -f database.sql
