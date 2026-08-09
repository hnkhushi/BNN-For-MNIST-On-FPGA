import torch
from torchvision import datasets, transforms

# Load the MNIST test dataset
transform = transforms.ToTensor()

test_dataset = datasets.MNIST(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

# Select an image (change the index as needed)
index = 420
image, label = test_dataset[index]

print("True Label:", label)
print("Image shape:", image.shape)   # torch.Size([1, 28, 28])
pix=torch.flatten(image)
print(pix.shape)
#print(pix[150:250])
img=[]
for i in pix:
    if i>=0.5:
        img.append("1")
    else:
        img.append("0")
print(''.join(img))

def bits_to_bytes(bits):
    """
    bits: list of 784 strings ('0'/'1')
    returns: list of 98 bytes
    """

    assert len(bits) == 784

    image = []

    for i in range(0, 784, 8):

        byte = 0

        for b in bits[i:i+8]:
            byte = (byte << 1) | int(b)

        image.append(byte)

    return image


def print_c_array(image):

    print("u8 image[98] =")
    print("{")

    for i in range(0,98,8):

        row = ", ".join(f"0x{x:02X}" for x in image[i:i+8])

        if i < 96:
            print(f"    {row},")
        else:
            print(f"    {row}")

    print("};")


image = bits_to_bytes(img)

print_c_array(image)
wt1=[]
layer2=[]
with open("fc1_binary.txt", "r") as f:
    with open("fc1_dirns.txt", "r") as f1:
        with open("fc1_thresholds.txt", "r") as f2:
            directions = [line.strip() for line in f1]
            thresh = [line.strip() for line in f2]
            for k, line in enumerate(f):
                arr = []
                wt1=line.split()
                #print("weights",wt1[0:10])
                for i in range(len(wt1)):
                    arr.append(int(wt1[i]==img[i]))
                #print("xnor result",arr)
                pcount = 0
                for j in range(len(arr)):
                    pcount+=arr[j]
                #print("pcount",pcount)
                prod=2*pcount-784
                #print("prod",prod)
                if directions[k]=="1":
                    if prod>=int(thresh[k]):
                        layer2.append("1")
                    else:
                        layer2.append("0")
                else:
                    if prod<=int(thresh[k]):
                        layer2.append("1")
                    else:
                        layer2.append("0")

#print(len(layer2))
#print(layer2)
#print(len(img))
#print("image",img[0:10])
#print("layer2",layer2)
#print(len(layer2))
#signed [$clog2(2*WIDTH+1)-1:0]
wt2=[]
layer3=[]
with open("fc2_binary.txt", "r") as file:
    with open("fc2_dirns.txt", "r") as file1:
        with open("fc2_thresholds.txt", "r") as file2:
            directions2 = [line.strip() for line in file1]
            thresh2 = [line.strip() for line in file2]
            for k, line in enumerate(file):
                arr = []
                wt2=line.split()
                #print("weights",wt2[0:10])
                for i in range(len(wt2)):
                    arr.append(int(wt2[i]==layer2[i]))
                #print("xnor result",arr[0:10])
                pcount = 0
                for j in range(len(arr)):
                    pcount+=arr[j]
                #print("pcount",pcount)
                prod=2*pcount-256
                #print("prod",prod)
                if directions2[k]=="1":
                    if prod>=int(thresh2[k]):
                        layer3.append("1")
                    else:
                        layer3.append("0")
                else:
                    if prod<=int(thresh2[k]):
                        layer3.append("1")
                    else:
                        layer3.append("0")
#print(layer3)
wt3=[]
layer4=[]
with open("fc3_binary.txt", "r") as f:
    for line in f:
        arr = []
        wt3=line.split()
        #print("weights",wt3[0:5])
        for i in range(len(wt3)):
            arr.append(int(wt3[i]==layer3[i]))
        #print("xnor result",arr[0:5])
        pcount = 0
        for j in range(len(arr)):
            pcount+=arr[j]
        #print("pcount",pcount)
        prod=2*pcount-256
        #print("prod",prod)
        layer4.append(prod)

#print(len(layer4))
#print(layer4)
print("predicted output",layer4.index(max(layer4)))
#print(len(layer3))
#print(layer3[0:10])
#print(len(img))
#print("input",layer2[0:10])
