import mysql.connector
from apps.auth import *

# Load .env
load_dotenv()

# Connect to MySQL
mydb = mysql.connector.connect(
  host= os.getenv("DB_HOSTS"),
  user= os.getenv("DB_USERS"),
  password= os.getenv("DB_Password"),
  database= os.getenv("DB_NAMES")
)

cursor = mydb.cursor()


# 2. RoleID will be below listed
create_role_table = """
CREATE TABLE IF NOT EXISTS `role` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE);"""
cursor.execute(create_role_table)

# # Insert roles in role table
insert_roles_in_role_table = """
INSERT INTO `role` (`name`) VALUES (%s), (%s);
"""
cursor.execute(insert_roles_in_role_table, ('Admin', 'Normal User'))



# # 1. Create a database table "user" in MySQL with below details 
create_user_table = """
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `profilepic` VARCHAR(255) DEFAULT NULL,
    `name` VARCHAR(100) NOT NULL,
    `cellnumber` VARCHAR(15) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `deletedAt` DATETIME DEFAULT NULL,
    `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `roleId` INT UNSIGNED NOT NULL,
    FOREIGN KEY (`roleId`) REFERENCES `role`(`id`)
);
"""
cursor.execute(create_user_table)


# Insert admin user
insert_user_query = """
INSERT INTO `user` 
(`profilepic`, `name`, `cellnumber`, `password`, `email`, `roleId`) 
VALUES (%s, %s, %s, %s, %s, %s);
"""

get_admin_pass = os.getenv("Admin_password")
get_admin_email = os.getenv("Admin_Email")
encrypt_pass_get = encrypted_password(get_admin_pass)

user_data = (
    None,                        # profilepic
    "Admin User",                # name
    "8866349316",                # cellnumber
    encrypt_pass_get,             # password (normally store a hashed password)
    "suflaam@admin.com",         # email
    1                            # roleId (Admin role id)
)


cursor.execute(insert_user_query, user_data)

# accesstoken table create
create_access_token_table = """
        CREATE TABLE IF NOT EXISTS accesstoken (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            token TEXT NOT NULL,
            ttl DATETIME NOT NULL,
            userId INT UNSIGNED NOT NULL,
            created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userId) REFERENCES user(id)
        );
        """
cursor.execute(create_access_token_table)

mydb.commit()
cursor.close()
mydb.close()

