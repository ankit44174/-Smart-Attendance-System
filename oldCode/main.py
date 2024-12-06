import recorded2, program

cmd = int(input("Press 1 for Live caputre \n \t OR \nPress 2 to caputre from recorded video"))

if cmd == 1:
    program.main()
else:
    recorded2.func1()
