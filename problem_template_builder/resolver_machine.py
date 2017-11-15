from Constants import Constants
import matlab_grading_service
from google_service import gsheets

class resolver_machine():
    
    APIAddress = Constants(
        NONE="", 
        MATLAB="120.72.83.82:8080", 
        EXCEL="",
        CPLUSPLUS="",
        JAVA="",
        CSHARP="",
        Default="")

    APIURL = Constants(
        NONE="/none", 
        MATLAB="/check",
        EXCEL="/none",
        CPLUSPLUS="/none",
        JAVA="/none",
        CSHARP="/none",
        Default="/none")

    NAME = Constants(
        NONE="none", 
        MATLAB="matlab",
        EXCEL="gsheet",
        CPLUSPLUS="c++",
        JAVA="java",
        CSHARP="c#",
        Default="none")

    NAME_INTEGER = Constants (
        NONE = 0,
        MATLAB = 1
        )

    def getResolverAddress(self, query):
        if query == self.APIAddress.MATLAB:
            return self.APIAddress.MATLAB
        elif query == self.APIAddress.NONE:
            return self.APIAddress.NONE
        else:
            return self.APIAddress.NONE

    def getResolverURL(self, query):
        if query == self.APIURL.MATLAB:
            return self.APIURL.MATLAB
        elif query == self.APIURL.NONE:
            return self.APIURL.NONE
        else:
            return self.APIURL.NONE

    def getDefaultAddress(self):
        return self.APIAddress.NONE

    def getDefaultURL(self):
        return self.APIURL.NONE

    def getDefaultResolver(self):
        return self.NAME.NONE

    def syncCall(self, resolver, teacher_answer, student_answer):
        result = False
        if resolver == self.NAME.NONE:
            print "self.NAME.NONE"
            result =  False
        elif resolver == self.NAME.MATLAB:
            print "self.NAME.MATLAB:"
            result = matlab_grading_service.evaluate_matlab_answer(self.APIAddress.MATLAB, self.APIURL.MATLAB, teacher_answer, student_answer)
        elif resolver == self.NAME.EXCEL:
            print "self.NAME.EXCEL:"
            gsheet = gsheets()
            result = gsheet.check_answer(teacher_answer, student_answer)
        else:
            print "self.NAME.OTHER:"

        return result
    
if (__name__ == "__main__"):
    # Usage example.
    #Nums = Constants(
    #    ONE=1, 
    #    PI=3.14159, 
    var = resolver_machine()
    check = resolver_machine.APIAddress.MATLAB
    test = var.getResolverAddress(check)
    print test
    print '----- Following line is deliberate ValueError -----'
            
        
    
    
    
    
    
    
