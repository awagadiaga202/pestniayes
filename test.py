from decouple import config

print("SECRET_KEY =", config('SECRET_KEY'))
