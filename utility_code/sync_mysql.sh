#!/bin/bash
namespace="$1"
rm -f /home/epic/5_SCRATCH/dump.sql
mysqldump -uroot -p$MARIADB_ROOT_PASSWORD --all-databases --skip-lock-tables --result-file=/home/epic/5_SCRATCH/dump.sql --host=mysql.play --ignore-database=plan
echo 'DROP TABLE IF EXISTS `mysql`.`global_priv`;' | mysql -uroot -p$MARIADB_ROOT_PASSWORD --host=mysql.$namespace
echo 'DROP VIEW IF EXISTS `mysql`.`user`;' | mysql -uroot -p$MARIADB_ROOT_PASSWORD --host=mysql.$namespace
mysql -uroot -p$MARIADB_ROOT_PASSWORD --host=mysql.$namespace < /home/epic/5_SCRATCH/dump.sql
echo 'flush privileges;' | mysql -uroot -p$MARIADB_ROOT_PASSWORD --host=mysql.$namespace
