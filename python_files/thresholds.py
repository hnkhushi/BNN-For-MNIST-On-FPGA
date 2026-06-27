import torch
import math
bn = torch.load("batchnorm_params.pt")
print(bn.keys())
gamma1 = bn["bn1_gamma"]
beta1  = bn["bn1_beta"]
mean1  = bn["bn1_mean"]
var1   = bn["bn1_var"]

gamma2 = bn["bn2_gamma"]
beta2 = bn["bn2_beta"]
mean2  = bn["bn2_mean"]
var2   = bn["bn2_var"]
print('raw values')
print(gamma2)
with open("fc1_thresholds.txt", "w") as f:
    with open("fc1_dirns.txt", "w") as file:
        for i in range(256):
            gamma=gamma1[i].item()
            beta=beta1[i].item()
            mean=mean1[i].item()
            var=var1[i].item()
            th=mean - (beta * math.sqrt(var + 1e-5)) / gamma
            thresh=round(th)
            f.write(f"{thresh}\n")
            if gamma>=0:
                file.write(f"{1}\n")
            else:
                file.write(f"{0}\n")

with open("fc2_thresholds.txt", "w") as f1:
    with open("fc2_dirns.txt", "w") as file1:
        for j in range(256):
            gamma=gamma2[j].item()
            beta=beta2[j].item()
            mean=mean2[j].item()
            var=var2[j].item()
            th1=mean - (beta * math.sqrt(var + 1e-5)) / gamma
            thresh1=round(th1)
            f1.write(f"{thresh1}\n")
            if gamma>=0:
                file1.write(f"{1}\n")
            else:
                file1.write(f"{0}\n")