import httplib
import json
 
 
def evaluate_matlab_answer(matlab_server_url, matlab_solver_url, teacherAns, studentAns):
 
    print matlab_server_url + matlab_solver_url
    conn = httplib.HTTPConnection(matlab_server_url)
    headers = { "Content-Type": "application/json" }
    body = json.dumps({"teacherAns": teacherAns, "studentAns" : studentAns})
    conn.request("POST", matlab_solver_url, body, headers)
    
    print matlab_server_url + matlab_solver_url
    
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
#    studentAns = "A =[ 2, 1, 1 ; -1, 1, -1 ; 1, 2, 3] \n B = [ 2 ; 3 ; -10] \n  InvA = inv(A) \n  X=InvA * B"
    studentAns = "A =[ 21, 1, 1 ; -1, 1, -1 ; 1, 2, 3] \n B = [ 2 ; 3 ; -10] \n  InvA = inv(A) \n  X=InvA * B" # Wrong answer
    
    result = evaluate_matlab_answer(matlab_server_url, matlab_solver_url, teacherAns, studentAns)
    print 'result = ' + str(result)
