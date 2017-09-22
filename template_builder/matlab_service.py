import httplib
import json
 
 
def evaluate_matlab_answer(matlab_server_url, matlab_solver_url, teacherAns, studentAns):
 
    print "Matlab problem solver: " + matlab_server_url + matlab_solver_url
    print "Teacher's answer:\n" + teacherAns
    print "Student's answer:\n" + studentAns

    conn = httplib.HTTPConnection(matlab_server_url)
    headers = { "Content-Type": "application/json" }
    body = json.dumps({"teacherAns": teacherAns, "studentAns" : studentAns})
    conn.request("POST", matlab_solver_url, body, headers)
    
    response = conn.getresponse()
    if response.status == 200:
       result = json.loads(response.read())
       # print 'RESULT: ' + str(result)
       return result
    else:
        return False # error
    
    
if __name__ == "__main__":
    matlab_server_url = '120.72.83.82:8080'
    matlab_solver_url = '/check'
    
    teacherAns =  "A =[ 2, 1, 1 ; -1, 1, -1 ; 1, 2, 3] \n B = [ 2 ; 3 ; -10] \n  InvA = inv(A) \n  X=InvA * B"
    studentAns = "A =[ 2, 1, 1 ; -1, 1, -1 ; 1, 2, 3] \n B = [ 2 ; 3 ; -10] \n  InvA = inv(A) \n  X=InvA * B"
    # studentAns = "A =[ 21, 1, 1 ; -1, 1, -1 ; 1, 2, 3] \n B = [ 2 ; 3 ; -10] \n  InvA = inv(A) \n  X=InvA * B" # Wrong answer

    teacherAns = "sum= 9 + 10\nprod = 10 * 9"
    studentAns = "sum= 9 +10 \n prod = 10 * 9"
    
    result = evaluate_matlab_answer(matlab_server_url, matlab_solver_url, teacherAns, studentAns)
    print 'result = ' + str(result)
