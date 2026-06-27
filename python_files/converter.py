arr1=[]
with open("fc1_weights.txt", "r") as f:
    with open("fc1_binary.txt", "w") as file:
        for x in f:
            arr1=x.strip().split()
            line1=[]
            for i in arr1:
                if i=="-1":
                    line1.append("0")
                else:
                    line1.append("1")
            file.write(" ".join(line1)+"\n")


arr2=[]
with open("fc2_weights.txt", "r") as f:
    with open("fc2_binary.txt", "w") as file:
        for x in f:
            arr2=x.strip().split()
            line2=[]
            for i in arr2:
                if i=="-1":
                    line2.append("0")
                else:
                    line2.append("1")
            file.write(" ".join(line2)+"\n")

arr3=[]
with open("fc3_weights.txt", "r") as f:
    with open("fc3_binary.txt", "w") as file:
        for x in f:
            arr3=x.strip().split()
            line3=[]
            for i in arr3:
                if i=="-1":
                    line3.append("0")
                else:
                    line3.append("1")
            file.write(" ".join(line3)+"\n")