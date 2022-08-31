from z3 import *
import itertools
import numpy as np

def count_neg(ref, xs):
    s = 0
    for x in xs:
        s += If(x <= ref, 1, 0)
    return s

### Filter the existing variables by timeslot
def give_timeslot(parameter):
    
    return int(str(parameter).split("_")[2])

### Defining variables

def main():
    weekdays = 5
    timeslots = 4
    max_classes = 3
    rooms = 3
    classes = 12
    
### Schedule grid
    s = Optimize()
    X = [[[Int("x_%s_%s_%s" % (j, i, k)) for j in range(rooms)]for i in range(timeslots)]for k in range(weekdays)]

### Constraint to have 1 class in 1 room in 1 timeslot
    merged = list(itertools.chain.from_iterable(X))
    merged = list(itertools.chain.from_iterable(merged))
    for i in range(classes):
        s.add(AtLeast(*[merged[idx] == i+1 for idx in range(0, len(merged))], 1))
        s.add(AtMost(*[merged[idx] == i+1 for idx in range(0, len(merged))], 1))

### Every class happens only once a week
    for i in range(0, len(merged)):
        s.add(merged[i] < classes+1)
        s.add(merged[i] >= 0)


    for day in range(weekdays):
        for slot in range(timeslots):
            s.add(AtMost(*[X[day][slot][room] != 0 for room in range(rooms)], 1))

    for i in merged:
        if give_timeslot(i)==0:
            s.add_soft(i == 0)

    for day in range(0,len(X)):
        s.add_soft(AtLeast(*[Sum(all_rooms) == 0 for all_rooms in X[day]], classes-max_classes))



    s.check()
    m = s.model()
    sol = [[[m[X[x][y][z]].as_long() for z in range(rooms)] for y in range(timeslots)]for x in range(weekdays)]
    print("Report:")
    print("Number of classes: "+str(classes))
    print("Days in the week:"+str(weekdays))
    print("Timeslots per day: "+str(timeslots))
    print("Number of Rooms: "+str(rooms))
    print("soft requirements:")
    print(" - no classes in first period")
    print(" - no more than 3 classes per day per student*")
    print(" * since schedules have not been implemented that just means 3 classes per day")
    print("------------------")
    print("This weeks schedule:")
    for day, sched in zip(["Monday,  ", "Tuesday,", "Wednesday,", "Thursday,", "Friday,   "], sol):
        for slot, s in zip(["16:20-17:50", "18:00-19:30", "19:40-21:10", "21:30-24:00"], sched):
            for room,i in zip(["Room 1", "Room 2", "Room 3"], s):
                if int(i) != 0:
                    print("Class "+str(i)+",\t On "+day+"\t\t"+slot+", in: "+room)


if __name__ == '__main__':
    main()

