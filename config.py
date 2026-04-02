class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///university.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "my-secret-key-123"
    ALL_PERMISSIONS = {
        "students_page": ["create", "read", "update", "delete"],
         "teachers_page": ["create", "read", "update", "delete"]
                       }
    
