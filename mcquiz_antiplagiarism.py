#Assumed 18 column csv file with columns [ OrgDefinedId, Username, FirstName, LastName, Attempt #, Attempt Start,
#Attempt End, Section #, Q #, Q Type, Q Title, Q Text, Bonus?, Difficulty, Answer, Answer Match, Score, Out Of ]

import csv, os, sys, argparse, copy


#DEFINED THRESHOLDS
parser = argparse.ArgumentParser()
parser.add_argument("csvdata",help="csv file to parse from MyCourses")
args = parser.parse_args()

filename = args.csvdata

#leave empty array if you want to run on all submissions or write in the student IDs to only consider this subset

#student_ids = []
student_ids = [ "260886004","260969793","260972779","260972919","260983564","260928704","260889002",
                "260884831","260835202","260854962","260966402","260977955","260894577","260896488",
                "260896999","260911839","260888163","260931941","260948291","260896124","260838711",
                "260864180","260838194","260894909","260902910","260908788","260904138","260788127",
                "260914692","260910714","260888079","260906748","260950354","260969453","260950146","260956368" ]

ultra = {}; #the dictionary of everything
cqt_list = [] 
nt_list = []



print( "Reading data...")

with open(filename, newline='') as csvfile:
    i=0
    lastDirName = ""
    lastFileName = ""
    lastStudentID = ""
    lastQuestionNum= -1
    master_dict = {}
    included_cols = [0, 1, 8, 11, 14, 15, 16] # cols we need ['OrgDefinedId', 'Username', 'Q #', 'Q', 'Answer', 'Answer Match', 'Score']
    spamreader = csv.reader(csvfile, delimiter=',') #read csv line delimit on comma
    
    for row in spamreader:
        content = list(row[i] for i in included_cols)
        if(content[0] == "OrgDefinedId"): #exclude first line
            continue

        #define output structure as results/studentID_mcgillEmail/result.txt
        newDirName = "results/" + content[0] + "_" + content[1]
        newFileName = newDirName + "/result.txt"
        newStudentID = str(content[0])

        
        if(content[2] != '' and ( student_ids == [] or str(content[0]) in student_ids ) ): #skip invalid lines
            if(lastDirName == ""):
                lastDirName = "results/" + content[0] + "_" + content[1]

            if(lastFileName == ""):
                lastFileName = lastDirName + "/result.txt"

            if(lastStudentID == ""):
                lastStudentID = str(content[0])

            if(newFileName != lastFileName): #new person, write contents of master_dict into a file
                if not os.path.exists(lastDirName): #make a directory for each student
                    os.makedirs(lastDirName)

                if(master_dict.keys() != []): #master_dict of previous person is filled, update ultra dict
                    ultra[lastStudentID] = {}
                    ultra[lastStudentID] = copy.deepcopy(master_dict)
                    master_dict.clear() #clear for next person
                    
                lastDirName = newDirName
                lastFileName = newFileName
                lastStudentID = newStudentID

            #make new master_dict entry with empty data for each new question
            if(lastQuestionNum != content[2]):
                lastQuestionNum = content[2]
                master_dict[str(content[3])] = {}
            
            master_dict[str(content[3])][str(content[4])] = (str(content[5]),str(content[6])) #store the csv line in master_dict

    #append last student
    ultra[lastStudentID] = {}
    ultra[lastStudentID] = copy.deepcopy(master_dict)
    master_dict.clear() 
    
    '''
    i+=1
    if i == 1000: #Consider only first 1000 lines from csv file for debugging
        break
    '''
print("Done!")



#GENERATE TABLES 
print("Generating table...")

done_counter = 1
#scenarios: question common
for row_key in ultra.keys():
    qset1 = ultra[ row_key ].keys()
    
    print("Creating folder for student " +str( row_key ) + "...   " + str(done_counter) + "/" + str(len(ultra.keys())))
    done_counter += 1
          
    for col_key in ultra.keys(): #skip files for the same student
        if( str(col_key) == str(row_key) ):
            continue
        
        qset2 = ultra[ col_key ].keys()
        
        subfolder_name = "table/" + str(row_key) + "/"
        if not os.path.exists(subfolder_name): #make folder for every student
            os.makedirs(subfolder_name)

        fname = subfolder_name + str(row_key) + "-" + str(col_key) + ".txt"
        f = open(fname, "w")
        f.write( str(row_key) + "-" + str(col_key) + "\n\n" ) #top row of student ID info

        q_counter = 1
        common_questions_counter = 0
        
        for question in qset1: #loop through all questions for student1
            f.write(str(q_counter))

            q_counter += 1
            
            ans_correct_counter_s1 = 0
            total_ans_counter_s1 = 0
            
            for ans in ultra[ row_key ][ question ].keys(): #determine if student1 had correct or incorrect answer
                ans_correct_counter_s1 += float(ultra[ row_key ][ question ][ans][ 1 ])
                total_ans_counter_s1 += 1

            if ans_correct_counter_s1 == total_ans_counter_s1 and total_ans_counter_s1 != 0: #correct answer
                f.write( "C" )
            elif ans_correct_counter_s1 == 0:
                f.write( "W" )
            else:
                f.write( "PC" ) #partially correct, not sure if there were questions with partial answer points
                
                
            if( question in qset2 ): #if common
                f.write( " - " + str( 1 + list(qset2).index( question ) ) ) #offset index by 1 for human read
                common_questions_counter += 1

                ans_correct_counter_s2 = 0
                total_ans_counter_s2 = 0

                for ans in ultra[ col_key ][ question ].keys(): #determine if student2 had correct or incorrect answer
                    ans_correct_counter_s2 += float(ultra[ col_key ][ question ][ans][ 1 ])
                    total_ans_counter_s2 += 1

                if ans_correct_counter_s2 == total_ans_counter_s2 and total_ans_counter_s2 != 0: #correct answer
                    f.write( "C\n" )
                elif ans_correct_counter_s2 == 0:
                    f.write( "W\n" )
                else:
                    f.write( "PC\n" ) #partially correct, not sure if there were questions with partial answer points

            else: #questions not common
                f.write( " - NP\n" )


        #do statistics 
        common_questions = list(set(qset1).intersection(qset2))

        common_ans_counter = 0
        total_ans_counter = 0

        common_questions_same_ans_both_correct = 0
        common_questions_same_ans_both_wrong = 0
        common_questions_diff_answers = 0
            
        for cq in common_questions:
                
            answer_keys = ultra[ row_key ][ cq ].keys()
            total_ans_counter += len( answer_keys )
                
            for ak in answer_keys:
                try:
                    if( ultra[ row_key ][cq][ak][0] == ultra[ col_key ][cq][ak][0] ): #same answer
                        common_ans_counter += 1

                        if( str(ultra[row_key][cq][ak][1]) == "0" and str(ultra[col_key][cq][ak][1]) == "0"): #same incorrect
                            common_questions_same_ans_both_wrong += 1
                        elif( str(ultra[row_key][cq][ak][1]) == "1" and str(ultra[col_key][cq][ak][1]) == "1"): #same correct
                            common_questions_same_ans_both_correct += 1    
                        else:
                            common_questions_diff_answers += 1 #different answer
                    else:
                        common_questions_diff_answers += 1
                except KeyError:
                    pass

        
        f.write( "\n\n-----STATISTICS-----\n")
        f.write( "Common questions among students: " + str(common_questions_counter) + "\n" )
        f.write( "Different answers on common questions: " + str( common_questions_diff_answers ) + "/" + str(total_ans_counter) + "\n" )
        f.write( "Common correct answers: " + str(common_questions_same_ans_both_correct) + "/" + str(total_ans_counter) + "\n" )
        f.write( "Common incorrect answers: " + str(common_questions_same_ans_both_wrong) + "/" + str(total_ans_counter) + "\n" )
        f.write( "Total common answers (correct+incorrect): " + str(common_questions_same_ans_both_correct+common_questions_same_ans_both_wrong) + "/" + str(total_ans_counter) + "\n" )
        
        f.write("\n")
        f.close()

print("Done!")






