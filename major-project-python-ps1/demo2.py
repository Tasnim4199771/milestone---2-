import pyhtml
#Student a 
import student_a_level_1
import student_a_level_2
import student_a_level_3

#Student b
import student_b_level_1
import student_b_level_2
import student_b_level_3

#In the studio project, the other team members would have their pages imported like this.
# import student_b_level_1
# import student_b_level_2
# import student_b_level_3

# import student_c_level_1
# import student_c_level_2
# import student_c_level_3

pyhtml.need_debugging_help=True

#attempt
# pyhtml.MyRequestHandler.pages["/"]=student_a_level_1; #Page to show when someone accesses "http://localhost/"
# pyhtml.MyRequestHandler.pages["/page2"]=student_b_level_1; #Page to show when someone accesses "http://localhost/page2"
# pyhtml.MyRequestHandler.pages["/page3"]=student_a_level_2; #Page to show when someone accesses "http://localhost/page3"
# pyhtml.MyRequestHandler.pages["/page4"]=student_a_level_2; #Page to show when someone accesses "http://localhost/page4"
# pyhtml.MyRequestHandler.pages["/page5"]=student_a_level_3; #Page to show when someone accesses "http://localhost/page5"
# pyhtml.MyRequestHandler.pages["/page6"]=student_b_level_3; #Page to show when someone accesses "http://localhost/page6"

pyhtml.MyRequestHandler.pages["/"]=student_a_level_1           #Home  
pyhtml.MyRequestHandler.pages["/page2"] = student_a_level_2    # Vaccination 
pyhtml.MyRequestHandler.pages["/page3"] = student_a_level_3    # Proogress
pyhtml.MyRequestHandler.pages["/page4"] = student_b_level_2    # Infection
pyhtml.MyRequestHandler.pages["/page5"] = student_b_level_1    # Mission
pyhtml.MyRequestHandler.pages["/page6"] = student_b_level_3    # Analysis 
#Host the site!


pyhtml.host_site()
