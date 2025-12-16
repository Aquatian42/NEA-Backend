import math

def mean(list):
    total = 0
    for i in list:
        total += i
    mean = total/len(list)
    return mean

def max(list):
    max = 0
    for i in list:
        if i > max:
            max = i
    return max

def min(list):
    min = 0
    for i in list:
        if i < min:
            min = i
    return min

def standard_deviation(list):
    squares = []
    for i in list:
        squares.append(i**2)
    variance = mean(squares) - mean(list)**2
    standard_deviation = math.sqrt(variance)
    return standard_deviation