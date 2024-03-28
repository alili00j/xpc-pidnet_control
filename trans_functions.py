
from scipy.optimize import fsolve


def nonlinear_equations(x):
    # 定义非线性方程组
    x1, x2, x3, x4, x5 = x
    eq1 = x1 + 2*x2 - 3*x3 + 4*x4 - 5*x5 - 10 # 其他方程的定义
    eq2 = x1 + 2*x2 - 3*x3 + 4*x4 - 5*x5 - 10
    eq3 = x1 + 2*x2 - 3*x3 + 4*x4 - 5*x5 - 10
    eq4 = x1 + 2*x2 - 3*x3 + 4*x4 - 5*x5 - 10
    eq5 = x1 + 2*x2 - 3*x3 + 4*x4 - 5*x5 - 10
   
    return [eq1,eq2,eq3,eq4,eq5]

def transform_vision_position(line1,line2,node_center,othter_information):
    #line=[a,b],node=[x,y],other_information=f(焦距)
    #将五个未知数合并
    

    roll,yaw,pitch,high,corner=0,0,0,0,0
    x=roll,yaw,pitch,high,corner
    solution = fsolve(nonlinear_equations, x)
    roll,yaw,pitch,high,corner=solution
    return roll,yaw,pitch,high,corner#侧偏