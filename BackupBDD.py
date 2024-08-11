from conection import Conect
from props import realizar_backup



con = Conect()
path = "/home/ubuntu/outputdb/"

realizar_backup(con.user, con.db, path)