'''
File: autoD.py
Description: Forward automatic differentiation version3.5.0
History:
    Date    Programmer SAR# - Description
    ---------- ---------- ----------------------------
  Author: dwindz 24Feb2016           - Created
  Author: dwindz 25Feb2016           - v2
                                        -include multi-variable entry
  Author: dwindz 03May2016           - v2.1
                                        -change x and dOrder inputs to type dict
                                        -corrected Multiply, Power etc. on value of new differntiation order
                                        -corrected change multiplication to numpy.dots
  Author: dwindz 18May2016           - v3
                                        -corrected bug in Power where power goes to -1 from 0
                                        -add dependent scalars to reduce runtime
  Author: dwindz 19May2016           - v3.1
                                        -remove class creation inside class function to reduce runtime
                                        -Multiply and Addition now accepts floats as one of the object in list
  Author: dwindz 03Jun2016           - v3.2
                                        -added complex conjugate, real and imaginary
                                        -added shortcut method __add__ etc
  Author: dwindz 13Dec2016           - v3.3
                                        -added absolute
  Author: dwindz 02Jan2017           - v3.4
                                        -added hyperbolic trigo functions
  Author: dwindz 03Jan2017           - v3.5
                                        -added debug print out
                                       

'''

'''
Standardized class def: 
func            class object      class object must contain the following function
                                    def cal(self,x,dOrder):
                                        x        dict[identifier]=float
                                        dOrder   dict[identifier]=int
                                        return float results or call to other class object .cal function

Note:
I divided the Class into three types; basic functions, base-end functions and flexible functions.
Basic functions contain class objects that deals with differentiating operations
Base end functions returns the result for any order of differentiation without call to other functions.
Flexible functions accepts user-defined function and turn them into callable objects "func" in this module.


'''

import numpy as np
'''
--------------------Main Class-----------------
'''   
class AD:
    def defaultDebugSwitch(x,dOrder,result):
        return True
    debugPrintout=False
    debugName=''
    debugSwitch=defaultDebugSwitch
    def __pow__(self, val):
        return Power(self,val)
    def __rpow__(self, val):
        return Power(val,self)
    def __add__(self, val):
        return Addition([self,val])
    def __radd__(self, val):
        if val == 0:
            return self
        else:
            return Addition([self,val])
    def __sub__(self, val):
        return Addition([self,Multiply([-1.,val])])
    def __rsub__(self,val):
        return Addition([val,Multiply([-1.,self])])
    def __mul__(self, val):
        return Multiply([self,val]) 
    def __rmul__(self, val):
        if val == 1:
            return self
        else:
            return Multiply([self,val])
    def __truediv__(self, val):
        return Multiply([self,Power(val,-1)])
    def __rtruediv__(self, val):
        return Multiply([val,Power(self,-1)])
    def __neg__(self):
        return Multiply([-1.,self])
    def debugOn(self,name=debugName):
        self.debugPrintout=True
        self.debugName=name
        return;
    def debugOff(self):
        self.debugPrintout=False
        return;
    def debugPrint(self,x,dOrder,result):
        if self.debugPrintout and self.debugSwitch(x,dOrder,result):
            print(self.debugName,'@',x)
            print('    differential=',dOrder)
            print('    value=',result)
        return;
    
    
        
'''
#---------------Basic Functions-------------------------------#
'''

class Differentiate(AD):
    def __init__(self,func,order):
        self.inputFunc=func
        self.inputorder=order
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def cal(self,x,dOrder):
        new_dOrder=dOrder.copy()
        for var in self.inputorder:
            if var in dOrder:
                new_dOrder[var]=self.inputorder[var]+dOrder[var]
            else:
                new_dOrder[var]=self.inputorder[var]+0
        if 'ALL' not in self.dependent:
            for var in new_dOrder:
                if new_dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        result=self.inputFunc.cal(x,new_dOrder)
        self.debugPrint(x,dOrder,result)
        return result
        
class Addition(AD):
    def __init__(self,funcList):
        self.funcList=funcList
        for n in range(len(self.funcList)):
            if isinstance(self.funcList[n], (int, float,complex)):
                self.funcList[n]=Constant(self.funcList[n])
        self.dependent=[]
        for func in self.funcList:
            try:
                for dependent in func.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
            
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        temp=[]
        for n in range(len(self.funcList)):
            temp.append(self.funcList[n].cal(x,dOrder))
        result=sum(temp)
        self.debugPrint(x,dOrder,result)
        return result
              
class Multiply(AD):
    def __init__(self,funcList):
        self.funcList=[]
        self.coef=1.
        self.dependent=[]
        for func in funcList:
            if not(isinstance(func, (int, float,complex))):
                self.funcList.append(func)
            else:
                self.coef=self.coef*func
        for func in self.funcList:
            try:
                for dependent in func.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
        self.rdOL=rotatingdOrderList(len(self.funcList))
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        addList=[]
        pastCalculation={}
        if len(dOrderList)==0:
            mul=self.coef
            for n in range(len(self.funcList)):
                mul=mul*self.funcList[n].cal(x,{})
            self.debugPrint(x,dOrder,mul)
            return mul
        self.rdOL.reset(dOrderList)
        while not(self.rdOL.end):
            mul=self.coef
            temp_dOrderList=self.rdOL.get()
            for n in range(len(self.funcList)):
                pastCalculationKey=str(n)+' '+''.join(map(str,temp_dOrderList[n]))
                if pastCalculationKey in pastCalculation:
                    mul=mul*pastCalculation[pastCalculationKey]
                else:
                    temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                    temp_value=self.funcList[n].cal(x,temp_dOrder)
                    pastCalculation[pastCalculationKey]=temp_value
                    mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result

class Power(AD):
    def __init__(self,func,pow):
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        self.pow=pow 
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        if not(isinstance(self.pow, (int, float,complex))):
            self.new_exp=Exp(Multiply([Ln(self.func),self.pow]))
            try:
                for dependent in pow.dependent:
                    if dependent not in self.dependent:
                        self.dependent.append(dependent)
            except AttributeError:
                self.dependent=['ALL']
        else:
            self.new_exp=None
        self.rdOL=rotatingdOrderListPower()
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        if self.pow==1:
            result=self.func.cal(x,dOrder)
            self.debugPrint(x,dOrder,result)
            return result
        elif self.pow==0:
            self.debugPrint(x,dOrder,1.)
            return 1.
        elif not(self.new_exp==None):
            result=self.new_exp.cal(x,dOrder)
            self.debugPrint(x,dOrder,result)
            return result
        dOrderList,keyList=splitdOrder(dOrder)
        if len(dOrderList)==0:
            result=self.func.cal(x,dOrder)**self.pow
            self.debugPrint(x,dOrder,0.)
            return result
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    mul=mul*(self.pow-count)
                    count+=1
            if mul!=0:
                if (self.pow-count)!=0:
                    mul=mul*self.func.cal(x,{})**(self.pow-count)
                for n in range(len(temp_dOrderList)):
                    if len(temp_dOrderList[n])!=0:
                        pastCalculationKey=''.join(map(str, temp_dOrderList[n]))
                        if pastCalculationKey in pastCalculation:
                            mul=mul*pastCalculation[pastCalculationKey]
                        else:
                            temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                            temp_value=self.func.cal(x,temp_dOrder)
                            pastCalculation[pastCalculationKey]=temp_value
                            mul=mul*temp_value
                addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
    
class Exp(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        exp_value=np.exp(self.func.cal(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,exp_value)
            return exp_value
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func.cal(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)*exp_value
        self.debugPrint(x,dOrder,result)
        return result
        
class Ln(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        if len(dOrderList)==0:
            result=np.log(self.func.cal(x,{}))
            self.debugPrint(x,dOrder,result)
            return result
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    if count!=0:
                        mul=mul*count
                    count-=1
            mul=mul*self.func.cal(x,{})**count
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func.cal(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
        
class Log(AD):
    def __init__(self,func,base):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        self.base=base
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        if not(isinstance(self.base, (int, float,complex))):
            self.new_ln=Multiply([Ln(self.func),Power(Ln(self.base),-1.)])
            self.coef=1.
            for dependent in self.base.dependent:
                if dependent not in self.dependent:
                    self.dependent.append(dependent)
        else:
            self.new_ln=Ln(self.func)
            self.coef=-1./np.log(self.base)
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        result=self.coef*self.new_ln.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
            
class Cos(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        cosValue=np.cos(self.func.cal(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,cosValue)
            return cosValue
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        sinValue=np.sin(self.func.cal(x,{}))
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    count+=1
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func.cal(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            temp=count%4
            if temp==0:
                mul=mul*cosValue
            elif temp==1:
                mul=-mul*sinValue
            elif temp==2:
                mul=-mul*cosValue
            elif temp==3:
                mul=mul*sinValue
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
class Cosh(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.cosh=Cos(func*1j)
    def cal(self,x,dOrder):
        result=self.cosh.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Sin(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.rdOL=rotatingdOrderListPower()
    def cal(self,x,dOrder):
        if 'ALL' not in self.dependent:
            for var in dOrder:
                if dOrder[var]>0 and (var not in self.dependent):
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        dOrderList,keyList=splitdOrder(dOrder)
        sinValue=np.sin(self.func.cal(x,{}))
        if len(dOrderList)==0:
            self.debugPrint(x,dOrder,sinValue)
            return sinValue
        self.rdOL.reset(dOrderList)
        addList=[]
        pastCalculation={}
        cosValue=np.cos(self.func.cal(x,{}))
        while not(self.rdOL.end):
            mul=1.
            temp_dOrderList=self.rdOL.get()
            count=0
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    count+=1
            for n in range(len(temp_dOrderList)):
                if len(temp_dOrderList[n])!=0:
                    pastCalculationKey=''.join(map(str,temp_dOrderList[n]))
                    if pastCalculationKey in pastCalculation:
                        mul=mul*pastCalculation[pastCalculationKey]
                    else:
                        temp_dOrder=mergedOrder(temp_dOrderList[n],keyList)
                        temp_value=self.func.cal(x,temp_dOrder)
                        pastCalculation[pastCalculationKey]=temp_value
                        mul=mul*temp_value
            temp=count%4
            if temp==0:
                mul=mul*sinValue
            elif temp==1:
                mul=mul*cosValue
            elif temp==2:
                mul=-mul*sinValue
            elif temp==3:
                mul=-mul*cosValue
            addList.append(mul)
            self.rdOL.incr()
        result=sum(addList)
        self.debugPrint(x,dOrder,result)
        return result
class Sinh(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.sinh=-1j*Sin(func*1j)
    def cal(self,x,dOrder):
        result=self.sinh.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Tan(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.tan=Sin(func)/Cos(func)
    def cal(self,x,dOrder):
        result=self.tan.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
class Tanh(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
        self.tanh_negative=(1-Exp(-2.*func))/(1+Exp(-2.*func))
        self.tanh_positive=(Exp(2.*func)-1)/(Exp(2.*func)+1)
    def cal(self,x,dOrder):
        result=self.tanh_negative.cal(x,dOrder)
        if not(float('-inf')<np.abs(result)<float('inf')):
            result=self.tanh_positive.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
'''
#---------------Complex Functions-------------------------------#
'''
class Conjugate(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def cal(self,x,dOrder):
        result=np.conjugate(self.func.cal(x,dOrder))
        self.debugPrint(x,dOrder,result)
        return result
class Real(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def cal(self,x,dOrder):
        result=self.func.cal(x,dOrder).real
        self.debugPrint(x,dOrder,result)
        return result
class Imaginary(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def cal(self,x,dOrder):
        result=self.func.cal(x,dOrder).imag
        self.debugPrint(x,dOrder,result)
        return result
class Absolute(AD):
    def __init__(self,func):
        self.func=func
        if isinstance(func, (int, float,complex)):
            self.func=Constant(func)
        else:
            self.func=func
        self.abs=(Real(self.func)**2.+Imaginary(self.func)**2.)**0.5
        try:
            self.dependent=func.dependent[:]
        except AttributeError:
            self.dependent=['ALL']
    def cal(self,x,dOrder):
        result=self.abs.cal(x,dOrder)
        self.debugPrint(x,dOrder,result)
        return result
'''
#---------------Base End Functions-------------------------------#
'''
            
class Constant(AD):
    def __init__(self,const):
        self.const=const
        self.dependent=[]
    def cal(self,x,dOrder):
        for var in dOrder:
            if dOrder[var]>0:
                self.debugPrint(x,dOrder,0.)
                return 0.
                break
        else:
            self.debugPrint(x,dOrder,self.const)
            return self.const
         
class Scalar(AD):
    def __init__(self,name):
        self.name=name
        self.dependent=[name]
    def cal(self,x,dOrder):
        returnX=True
        for var in dOrder:
            if dOrder[var]>0:
                if var==self.name:
                    if dOrder[var]>1:
                        self.debugPrint(x,dOrder,0.)
                        return 0.
                    else:
                        returnX=False
                else:
                    self.debugPrint(x,dOrder,0.)
                    return 0.
        if returnX:
            self.debugPrint(x,dOrder,x[self.name])
            return x[self.name]
        else:
            self.debugPrint(x,dOrder,1.)
            return 1. 
'''
#---------------Flexible Functions-----------------#
'''
class Function(AD):
    def __init__(self,func,*args,dependent=['ALL']):
        self.func=func
        self.args=args
        self.dependent=dependent
    def cal(self,x,dOrder):
        args=self.args
        result=self.func(x,dOrder,*args)
        self.debugPrint(x,dOrder,result)
        return result
    def changeArgs(self,*new_args):
        self.args=new_args
        return;
    def checkArgs(self):
        return self.args

'''
--------------------Functions used-----------------
'''
def mergedOrder(dOrderList,keyList):
    newdOrder={}
    for ind in dOrderList:
        if keyList[ind] in newdOrder:
            newdOrder[keyList[ind]]+=1
        else:
            newdOrder[keyList[ind]]=1
    return newdOrder
def splitdOrder(dOrder):
    dOrderList=[]
    keyList=[]
    temp_dOrder=dOrder.copy()
    count=0
    for key in temp_dOrder:
        keyList.append(key)
        while temp_dOrder[key]>0:
            dOrderList.append(count)
            temp_dOrder[key]-=1
        count+=1
    return (dOrderList,keyList)
class rotatingdOrderList:
    def __init__(self,numOfFunc):
        self.rotatingList=[]
        self.dOrderList=[]
        self.dOrderListNum=0
        self.numOfFunc=numOfFunc
        self.end=False
    def reset(self,dOrderList):
        self.rotatingList=[]
        self.dOrderList=dOrderList
        self.dOrderListNum=len(dOrderList)
        for n in range(self.dOrderListNum):
            self.rotatingList.append(0)
        self.end=False
    def incr(self):
        ind=0
        count=True
        while not(self.end) and count:
            if self.rotatingList[ind]>=(self.numOfFunc-1):
                self.rotatingList[ind]=0
                if ind==(self.dOrderListNum-1):
                    self.end=True
                else:
                    ind+=1
            else:
                self.rotatingList[ind]+=1
                count=False
    def get(self):
        arrangeList=[]
        for n in range(self.numOfFunc):
            arrangeList.append([])
        for n in range(self.dOrderListNum):
            arrangeList[self.rotatingList[n]].append(self.dOrderList[n])
        return arrangeList
class rotatingdOrderListPower:
    def __init__(self):
        self.rotatingList=[]
        self.dOrderList=[]
        self.dOrderListNum=0
        self.numOfFunc=-1
        self.end=False
    def reset(self,dOrderList):
        self.rotatingList=[]
        self.dOrderList=dOrderList
        self.dOrderListNum=len(dOrderList)
        for n in range(self.dOrderListNum):
            self.rotatingList.append(0)
        self.end=False
        self.numOfFunc=self.dOrderListNum
    def incr(self):
        ind=0
        count=True
        while not(self.end) and count:
            if ind==(self.dOrderListNum-1):
                self.end=True
            elif self.rotatingList[ind]>max(self.rotatingList[(ind+1):]):
                self.rotatingList[ind]=0
                ind+=1
            else:
                self.rotatingList[ind]+=1
                count=False
    def get(self):
        arrangeList=[]
        for n in range(self.numOfFunc):
            arrangeList.append([])
        for n in range(self.dOrderListNum):
            arrangeList[self.rotatingList[n]].append(self.dOrderList[n])
        return arrangeList
                
