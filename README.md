# autoD
autoD is a lightweight, flexible automatic differentiation for python3 based on numpy. It enable user to convert your user-defined functions into differentiatable object. Thus, it will be able to do integration and matrix filling for you (see examples). To calculate the differential, call the function ".cal(x,dOrder)" of any class in this module, where 'x' is the value of independent scalars and 'dOrder' is the order of differentiation. Both 'x' and 'dOrder' are dictionaries.

###Function description:
#####Addition(funcList): objects in list can be float
input list of objects you want to add. funcList=[func1,func2,func3,...]

#####Multiply(funcList): objects in list can be float
input list of objects you want to multiply. funcList=[func1,func2,func3,...]

#####Power(func,pow):    
input an object and the power for power operation (pow can be a float or another func object).

#####Log(func,base):     
input an object and the base for logarithmic operation (base can be a float or another func object).

#####Exp(func):          
input object you want to do the operation e^.

#####Ln(func):           
input object you want to do the natural logarithmic operation.

#####Cos(func):          
input object you want to do the cosine operation.

#####Cosh(func):          
input object you want to do the hyperbolic cosine operation. (Dependent on Cos)

#####Sin(func):          
input object you want to do the sine operation.

#####Sinh(func):          
input object you want to do the hyperbolic sine operation. (Dependent on Sin)

#####Tan(func):          
input object you want to do the tangent operation. (Dependent on Sin and Cos)

#####Tanh(func):          
input object you want to do the hyperbolic tangent operation. (Dependent on Exp)
This function provides alternatives calculations to prevent value overflow.

#####Real(func):
input object you want to do discard the imaginary term.

#####Imaginary(func):
input object you want to do discard the real term.

#####Absolute(func):
input object you want to do find the absolute value.

#####Conjugate(func):
input object you want to do a complex conjugate

#####Constant(const):
change any float to a callable class object.

#####Scalar(name):
A scalar variable (each scalar must be independant of other variables)

#####Function(fx,*args,dependent='ALL'): 
input self-defined function to convert it to usable class object for differentiation.
Self-defined function must be able to accept the input in the form (x,dOrder,*args).
x is the value of the variable you want to differentiate wrt.
dOrder is the order of differentiation.
You can change your args even after definine by calling fx.changeArgs(*new_args).

###Past Versions
File 'autoD.py" represents the main and latest version. See inside file for version notes.

###note
I tried Theano (http://deeplearning.net/software/theano/) but I have no idea why it is clogging up my system RAM (~7GB, which is almost all I have). This code is easy to edit and depends on only Numpy. If you need more functionallity (I do not know what else there is to automatic differentiation as I have not explored Theano fully), want to include more functions or any other issues, please leave your comments :) . I am using python3, so I do not know how well it works for python2. Thanks.
