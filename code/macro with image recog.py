import cv2
import numpy as np
import pyautogui
import time
import os
from matplotlib import pyplot as plt
import math
import imutils
import win32api, win32con
import autoit

accuracy = 0
count = 0
top_left, bot_right = (0,0), (0,0)
x_biggest, y_biggest = 0,0
x_smallest, y_smallest = 9999,9999
x_top, y_top = 1054,626
x_bot, y_bot = 1251,676

# 720x1280	= 1054,626 , 1251,676
# 720x1560  = 1154,610 , 1335,654
# 1080x2300	= 1150,614 , 1334,659

#   standard deviation calculation from max value
def std(max_val, mean):
    return (max_val-mean)/3

#   gaussian distribution random using numpy from min and max value
def rand_gaus(min_val,max_val):
    # to prevent getting coordinate outside the button
    margin = (max_val - min_val) * 0.1
    max_val -= margin
    min_val += margin

    mean = (min_val+max_val)/2
    std_value = std(max_val,mean) # get the standard deviation using max_val
    # print("maxval:",max_val," ,minval:",min_val," ,mean:",mean," ,std:",std_value)
    return math.floor(np.random.normal(mean,std_value))

#   search image on screen
def imagesearch(image, scrn, precision=0.6):
    iteration = 0
    curr_iter = 0
    # get template image, grayscaled, and get canny edge
    template = cv2.imread(image, 0)
    template = cv2.Canny(template,50,200)
    tH, tW = template.shape[:2]

    # cv2.imshow("template after grayslaced and got the edge", template)
    # cv2.waitKey(0)

    # get screen image, grayscaled
    scrn_rgb = np.array(scrn)
    scrn_gray = cv2.cvtColor(scrn_rgb, cv2.COLOR_BGR2GRAY)
    found = None

    # loop from 100% to 20% in 20 times resizing
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        curr_iter += 1
        resized = imutils.resize(scrn_gray, width = int(scrn_gray.shape[1] * scale))
        ratio = scrn_gray.shape[1] / float(resized.shape[1])

        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        
        # get edged to the resized image
        edged = cv2.Canny(resized, 50, 200)
        res = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        # uncomment to visualize the step
        clone = np.dstack([edged,edged,edged])
        cv2.rectangle(clone, (max_loc[0], max_loc[1]), (max_loc[0] + tW, max_loc[1] + tH), (0,0,255), 2)
        cv2.imshow("visualize", clone)
        cv2.waitKey(0)

        # update the max correlation and top_left_coor if found the new one
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, ratio)
            iteration = curr_iter
    
    max_val, max_loc, ratio = found

    # check if it's below precision
    # if max_val < precision:
    #     return (-1, -1), (-1, -1)
    
    # get the coordinates of top left and bottom right
    x1, y1 = int(max_loc[0] * ratio), int(max_loc[1] * ratio)
    x2, y2 = int((max_loc[0] + tW) * ratio), int((max_loc[1] + tH) * ratio)
    print("correlation:", max_val, "| Box Position:", (x1,y1),",", (x2,y2), "| iter:",iteration)

    return (x1,y1), (x2,y2)

# imagesearch without edge and resizing
def imagesearch_classic(image, scrn, precision=0):
    #   get template image, grayscaled
    template = cv2.imread(image,0)
    template = cv2.Canny(template,50,200)
    tH, tW = template.shape[:2]

    # cv2.imshow("template", template)
    # cv2.waitKey(0)

    #   get screen image, grayscaled
    scrn_rgb = np.array(scrn)
    scrn_gray = cv2.cvtColor(scrn_rgb, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(scrn_gray, 50, 200)
    # print(scrn_rgb.shape)
    
    #   get edged to the resized image
    res = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    #   uncomment to visualize the step
    clone = np.dstack([edged,edged,edged])
    cv2.rectangle(clone, (max_loc[0], max_loc[1]), (max_loc[0] + tW, max_loc[1] + tH), (0,0,255), 2)
    cv2.imshow("visualize", clone)
    cv2.waitKey(0)
    
    # plt.subplot(1,2,1), plt.imshow(res, cmap='gray')
    # plt.title('Matching Result')
    # plt.xticks([]), plt.yticks([])
    
    # plt.subplot(1,2,2), plt.imshow(clone, cmap='gray')
    # plt.title('Detected Point')
    # plt.xticks([]),plt.yticks([])

    # plt.subplot(1,3,3), plt.imshow(template, cmap='gray')
    # plt.title('Template')
    # plt.xticks([]),plt.yticks([])
    # plt.show()


    #   check if it's below precision
    # print(max_val)
    #if max_val < precision:
    #    return (-1, -1), (-1, -1)
    
    # get the coordinates of top left and bottom right
    x1, y1 = int(max_loc[0]), int(max_loc[1])
    x2, y2 = int((max_loc[0] + tW)), int((max_loc[1] + tH))

    return (x1,y1), (x2,y2)

#   imagesearch but looped
def imagesearch_loop(image,duration,precision=0.8):
    top_left_loc, bot_right_loc = imagesearch(image,precision)
    while(top_left_loc[0] == -1):
        print("Not found yet")
        time.sleep(duration)
        top_left_loc = imagesearch(image,precision)
    return top_left_loc


#   function to click
def click_image(image, top_left_coor, bot_right_coor, action, duration=0):
    image = cv2.imread(image)
    x1,y1 = top_left_coor
    x2,y2 = bot_right_coor
    x_click = rand_gaus(x1,x2)
    y_click = rand_gaus(y1,y2)
    # print("x1:",x1,",y1:",y1,",x2:",x2,",y2:",y2)
    # print("x_click:",rand_gaus(x1,x2),",y_click:",rand_gaus(y1,y2))

    # print("x:",x_click)
    # print("y:",y_click)
    
    #   win32api and win32con : cant click on game
    # win32api.SetCursorPos((x_click,y_click))
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x_click,y_click,0,0)
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x_click,y_click,0,0)

    #   pyautogui : cant click on game
    pyautogui.moveTo(rand_gaus(x1,x2), rand_gaus(y1,y2), duration) # move cursor to X,Y over DURATION second(s)
    # pyautogui.click(button=action)

    #   pyautoit : cant click on game
    # autoit.mouse_click("left",x_click, y_click,1)
    global accuracy, count, x_top, y_top, x_bot, y_bot, x_smallest, y_smallest, x_biggest, y_biggest
    count += 1
    accuracy += 1 if((x_click>x_top and x_click<x_bot) and (y_click>y_top and y_click<y_bot)) else 0
    if(x_click < x_smallest): x_smallest = x_click
    if(x_click > x_biggest): x_biggest = x_click
    if(y_click < y_smallest): y_smallest = y_click
    if(y_click > y_biggest): y_biggest = y_click

#   image area search but colored
def imagesearch_colored(image,im):
    image = cv2.imread(image)
    im = np.array(im)
    res = cv2.matchTemplate(image,im,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_loc

#   image area search colored testing
# for i in range(100):
#     time1 = time.clock()
#     loc1 = imagesearch_colored(test_img,test_reg)
# print(str(time.clock() - time1) + " seconds (colored), Position: " + str(loc1))

img_dir = "images"
i = 0
mean = 0
time1 = time.clock()
while(i<1):
    # while(1):
    #    print(pyautogui.position())
    #    time.sleep(1)
    scrn = pyautogui.screenshot()
    for filename in os.listdir(img_dir):
        img = img_dir + "/" + filename
        top_left, bot_right = imagesearch(img,scrn)
        if(top_left[0] == -1):
            print(filename,"not found on the screen, continuing")
            continue
        else:
            click_image(img,top_left, bot_right,"left")
            break
    i+=1
    mean = (mean + (time.clock() - time1)) / i
print("total from", i, "tries:", str(time.clock() - time1), "seconds (gray scale)")
print("accuracy from", count, "registered:", float((accuracy/count) * 100),"%")
print("Smallest X:", x_smallest, ",biggest X:", x_biggest, ",smallest Y:", y_smallest, ",biggest Y:", y_biggest)
# print("Box position:", top_left, "|", bot_right)

# accuracy = 0
# count = 0
# i = 0
# mean = 0
# print("\nwithout edge")
# time1 = time.clock()
# while(i < 100):
#     scrn = pyautogui.screenshot()
#     for filename in os.listdir(img_dir):
#         img = img_dir + "/" + filename
#         top_left, bot_right = imagesearch_classic(img,scrn)
#         if(top_left[0] == -1):
#             print(filename,"not found on the screen, continuing")
#             continue
#         else:
#             click_image(img,top_left, bot_right,"right",0.2)
#             break
#     i+=1
#     mean = (mean + (time.clock() - time1)) / i
# print("mean times from 100 tries:", str(time.clock() - time1), "seconds (without edge and resizing)")
# print("accuracy from ", count, "registered:", float((accuracy/count) * 100),"%")