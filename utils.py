import math
import random
import bcrypt

def sum(list0):
    total = 0
    for i in list0:
        total += i
    return total

def mean(list1):
    total = sum(list1)
    mean = total/len(list1)
    return mean

def max(list2):
    max = 0
    for i in list2:
        if i > max:
            max = i
    return max

def min(list3):
    min = float("inf")
    for i in list3:
        if i < min:
            min = i
    return min

def standard_deviation(list4):
    squares = []
    for i in list4:
        squares.append(i**2)
    variance = mean(squares) - mean(list4)**2
    standard_deviation = math.sqrt(variance)
    return standard_deviation

def mse(test,correct):
    if len(test) != len(correct):
        print(len(test), len(correct))
        return("error")
    squares = []
    for i in range(len(test)):
        squares.append((test[i] - correct[i])**2)
    mse_value = mean(squares)
    return mse_value

def chunks_of_list(list5,number,length):
    out_lists = []
    input_length = len(list5) 
    for i in range(number):
        start_index = random.randint(0,input_length-length)
        end_index = start_index + length
        out_lists.append(list5[start_index:end_index])
    return out_lists



### passwords ###
def hash_password(pwd: str) -> str:
    # Hash a password and return it as a string
    password = pwd.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify a plain password against a hashed string
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False