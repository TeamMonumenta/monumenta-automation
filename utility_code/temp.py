#!/usr/bin/env pypy3

from lib_py3.library_of_souls import LibraryOfSouls

los = LibraryOfSouls("/home/epic/project_epic/server_config/data/plugins/all/LibraryOfSouls/souls_database.json")
los.upgrade_all()
los.save()
