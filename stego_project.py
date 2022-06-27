from stegano import lsb
from os.path import isfile,join

import time                                                                 #install time ,opencv,numpy modules
import cv2
import numpy as np
import math
import os
import shutil
from subprocess import call,STDOUT

def split_string(s_str,count=10):
    per_c=math.ceil(len(s_str)/count) # per_c = the first value greater then (length of the data being encoded / 10)
    c_cout=0 #
    out_str='' # string
    split_list=[] # dict
    for s in s_str: # for each letter in the encoded string
        out_str+=s # add the letter we're on to the output string
        c_cout+=1 # add one to our output list
        if c_cout == per_c: # if the number = the length
            split_list.append(out_str) # add the letter to the dictionary
            out_str='' #set the string to empty again
            c_cout=0 # reset the output counter
    if c_cout!=0:
        split_list.append(out_str) # if it doesnt equal 0 just add the character to the list
    return split_list

def frame_extraction(video):
    if not os.path.exists("./tmp"): #if the "tmp" directory doesnt exist
        os.makedirs("tmp") # make it
    temp_folder="./tmp" # ease of reference instead of having to put "./tmp" every time
    print("[INFO] tmp directory is created")

    vidcap = cv2.VideoCapture(video) # defines a video capture "object"
    count = 0

    while True:
        success, image = vidcap.read() # captures the video frame by frame
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image) # writes to the os.path, with the name of the file being a number which raises by one for each image and then writes the image data
        count += 1

def encode_string(input_string,root="./tmp/"):
    split_string_list=split_string(input_string) # the return of "split_string" is stored here
    for i in range(0,len(split_string_list)): # for the length of the list
        f_name="{}{}.png".format(root,i) # f_name equals the image name formatted from the temp directory and the integer
        secret_enc=lsb.hide(f_name,split_string_list[i]) # using the LSB library, we hide the character in the frame
        secret_enc.save(f_name) # then save the frame
        print("[INFO] frame {} holds {}".format(f_name,split_string_list[i]))
def decode_string(video):
    frame_extraction(video) # extract frames
    secret=[] # empty dict
    root="./tmp/"
    for i in range(len(os.listdir(root))): # listdir list all files and thus the length of that is how many files there is
        f_name="{}{}.png".format(root,i) # format each file
        secret_dec=lsb.reveal(f_name) # reveals the LSB for the file
        if secret_dec == None: # if there is nothing in the LSB, breaks the for loop because any relevant data has been extracted already
            break
        secret.append(secret_dec) # adds the letter hidden in the LSB to the dict
        
    print(''.join([i for i in secret])) # outputs the hidden message
    clean_tmp() # cleans the /tmp folder to save space 
def clean_tmp(path="./tmp"):
    if os.path.exists(path): # if it exists
        shutil.rmtree(path) # empty it
        print("[INFO] tmp files are cleaned up")

def main():
    input_string = input("Enter the input string :")
    f_name=input("enter the name of video")
    frame_extraction(f_name)
    call(["ffmpeg", "-i", f_name, "-q:a", "0", "-map", "a", "tmp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT) # command execution
    
    encode_string(input_string)
    call(["ffmpeg", "-i", "tmp/%d.png" , "-vcodec", "png", "tmp/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    
    call(["ffmpeg", "-i", "tmp/video.mov", "-i", "tmp/audio.mp3", "-codec", "copy", "video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    clean_tmp()

if __name__ == "__main__":
    while True:
        print("1.Hide a message in video 2.Reveal the secret from video")
        print("any other value to exit")
        choice = input()
        if choice == '1':
            main()
        elif choice == '2':
            decode_string(input("enter the name of video with extension"))
        else:
            break