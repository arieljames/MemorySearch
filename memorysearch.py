# memorysearch.py           6/23/08
#
# last modified 8/08/08
#
# John's first attempt to implement memory search

import pygame, os, sys, math, datetime
from pygame.locals import *
import random
from random import shuffle, choice
from operator import mod
from time import time  # for getting RTs

# Define colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,50)
ORANGE = (255,100,0)
BLUE = (50,150,255)
LIGHTBLUE = (100, 175, 255)
GRAY = (150,150,150)
DARKGRAY = (50, 50, 50)
DARKBLUE = (0,0,150) #(0, 0, 255)


random.seed(os.urandom(99))  # seed the random number generator

text_height = 36    # for ordinary text
stim_height = 72    # for memory set and probe
screen_height = 1000 # 768
screen_width = 1500 # 1024
mid_x = int(round(screen_width/2))
mid_y = int(round(screen_height/2))

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), HWSURFACE)
pygame.mouse.set_visible(0)
pygame.font.init()
# the font for messages to the subject
message_font = pygame.font.SysFont('times', text_height)
# teh font for the memory sets and probes
stim_font = pygame.font.SysFont('times', stim_height)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))


##subject_count_file = file('subject count.txt', 'r')
##subject_count = int(subject_count_file.read())
##subject_count_file.close()
##
##subject_number = subject_count + 1

# some useful functions (written by JEH)

def key_to_letter(key_val, key_mod=1):# mod=1 means upper-case; mod = 0 means lower-case
    # takes a key value as recorded by the event listner and returns the corresponding letter
    # a (and A) is key value 97; z (and Z) is key value 122
    #
    # first, conver the key value to the ASCII value: A = 65; Z is 90,
    #   so ASCII = key value minus 32
    if key_mod == 0: # lower case
        ascii = key_val
    elif key_mod == 1: # upper case
        ascii = key_val - 32
    else:
        print 'error in key_to_letter: key_mod = ',key_mod
        # sys.exit()
    if ascii < 256:
        return chr(ascii)
    else:
        return '' # return space is not a valid ascii value

def get_keypress(trigger=None):
    # this is my version
    # it waits for the user to enter a key in order to move on
    all_done = False
    while not all_done:
        event_list = pygame.event.get()
        for event in event_list:
            # process the_event according to what type of event it is
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                elif key_to_letter(event.key, event.mod) == trigger:
                    all_done = True
                elif trigger == None:
                    # if there's no trigger, then assume that the program
                    # wants to know what the user entered
                    all_done = True
                    return key_to_letter(event.key, event.mod)

def blit_text(message, line):
    # formats, renders and blits a message to screen on the designated line
    #   but does NOT update the screen.
    # it is for use in cases where it is necessary to put several lines of
    #   text on the screen
    # 1) render the message
    the_text  = message_font.render(message, True, BLUE, (250,250,250))
    # 2) set it's location
    text_rect = [1,line * text_height + 1,screen_width,text_height]
    # 3) blit it to the screen
    screen.blit(the_text, text_rect)

def get_response():
    # gets a stimulus present (P) or absent (A) response from the subject 
    # and returns the response and the RT
    #
    # the following is for getting RT
    start_time = time()
    
    all_done = False
    valid_trial = True  # set to false if subject's first response is not A or P
    # Get user input while un-paused
    while not all_done:
        event_list = pygame.event.get()
        for event in event_list:
            # process the_event according to what type of event it is
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                all_done = True # end the trial on the first response
                if event.key == K_ESCAPE:
                    sys.exit(0)
                else:
                    response = key_to_letter(event.key)
                if response in ['A','P']:
                    # Get RT
                    end_time = time()
                    RT = end_time - start_time
                    valid_trial = True
                    # print 'RT=',RT
                    screen.fill((250,250,250)) # blank the screen
                    pygame.display.update()
                    pygame.time.wait(1500) # wait 1500 ms before next trial
                    pygame.event.clear() # clear all events from the queue
                    return [response, RT, valid_trial]
                else:
                    # invald response: Inform subject of error
                    all_done = True
                    valid_trial = False
                    # clear the screen...
                    screen.fill((250,250,250))
                    error_message = response + ' is not a valid response.  Please respond only A or P.'
                    blit_text(error_message, 10)
                    blit_text('Press P or A to continue the experiment.',12)
                    pygame.display.update()
                    get_keypress()
                    pygame.event.clear() # clear all events from the queue
                    return [response, 0, valid_trial]

def mean_and_sd(data_vector):
    # takes one data vector and computes the mean and SD of the data therein
    mean = float(0.0)
    sd = float(0.0)
    n = len(data_vector)
    for datum in data_vector:
        mean += float(datum)
    if n > 0:
        mean = float(mean/n)
    for datum in data_vector:
        sd += float(pow(float(mean - datum), 2))
    if n > 0:
        sd = float(sd/n) # this is the Population (not sample) variance!
    sd = float(pow(sd, 0.5))
    return [mean, sd]

def make_memory_set(set_size):
    # makes a random memory set if size set_size by sampling without
    #   replacement from the set of integers (ASCII) values 65 ('A') to 90 ('Z')
    # the memory set is represente as a string, which Python also knows
    #   how to treat as a list, e.g., "in" and "len()" work on strings as
    #   well as other lists
    #
    memory_set = ''
    while len(memory_set) < set_size:
        ascii_val = 65 + int(round(random.random() * 25))
        new_letter = chr(ascii_val) # get the letter corresponding to the ascii value
        if not new_letter in memory_set:
            # this if statement does sampling w/o replacement
            memory_set = memory_set + new_letter
    return memory_set

def get_random_target(memory_set):
    # takes a memory set and returns a randomly-selected member of that set for
    #   use as a target (a "yes" response in the memory search)
    #
    # randomly choose an index up to len(memory_set) - 1
    index = int(round(random.random() * (len(memory_set) - 1)))
    return memory_set[index]

def get_random_distractor(memory_set):
    # takes a memory set and returns a randomly selected letter that is NOT
    #   a member of that memory set, i.e., a random distractor (i.e., a 'no'
    #   response on a memory search trial)
    all_done = False
    while not(all_done):
        ascii_val = 65 + int(round(random.random() * 25))
        if chr(ascii_val) not in memory_set:
            all_done = True
            return chr(ascii_val)

def fixation_cross():
    # displays a fixation cross in center of screen for 750 ms
    screen.fill((250,250,250))# GRAY)  # fill it with a middle gray...
    vertical_rect = [mid_x - 2, mid_y - 20, 4, 40]
    horizontal_rect = [mid_x - 20, mid_y - 2, 40, 4]
    screen.fill(BLACK, vertical_rect)   # the vertical leg of the cross
    screen.fill(BLACK, horizontal_rect) # the horizontal leg
    pygame.display.update()
    pygame.time.wait(750)
    
def display_memory_set(memory_set):
    # displays a memory set in center of screen for 750 ms per item
    screen.fill((250,250,250))# GRAY)  # fill it with a light gray...
    text_width = int(round(stim_height * len(memory_set)/4)) # center the memory set
    text_height = int(round(stim_height/4))
    wait_time  = 500 * len(memory_set) # display set for 500 ms per item
    text_rect = [mid_x - text_width, mid_y - text_height, text_width * 2, stim_height]
    the_text  = stim_font.render(memory_set, True, BLUE, (250,250,250))
    # blit it to the screen and then wait for wait_time ms
    screen.blit(the_text, text_rect)
    pygame.display.update()
    pygame.time.wait(wait_time)
    # blank the screen and wait 1500 ms
    screen.fill((250,250,250))# GRAY)  # fill it with a light gray...
    pygame.display.update()
    pygame.time.wait(1500) # was 500 ms
    
    
def display_probe(probe):
    # displays a memory set probe in center of screen until subject responds
    screen.fill((250,250,250))# GRAY)  # fill it with a light gray...
    text_width = int(round(stim_height/4)) # center the memory set
    text_rect = [mid_x - text_width, mid_y - text_width, stim_height, stim_height]
    the_text  = stim_font.render(probe, True, BLACK, (250,250,250))
    screen.blit(the_text, text_rect)
    pygame.display.update()


class Block(object):
    # contains the info necessary to specify the nature of a block
    #   of trials
    def __init__(self, index):
        self.index     = index  # order presented (1st, 2nd, etc.)
        self.trials    = [] # a record of which trials run in which order, plus data for each

class Trial(object):
    # contains the info about one trial:
    # which block target present/absent, how many distractors of each type,
    #   accuracy, validity (i.e.,valid response or not), and RT
    def __init__(self, block, memory_set_size, target_trial):
        self.block  = block   # a pointer to the block that owns this trial
        self.order  = 0       # order presented (1st, 2nd, etc.): compute at runtime
        self.memory_set = make_memory_set(memory_set_size)
        self.target_present = target_trial # True if probe in memory set, False if not
        if target_trial:
            # make the probe one of the items in the memory set
            self.probe = get_random_target(self.memory_set)
        else:
            # make the probe an itenm Not in the memory set
            self.probe = get_random_distractor(self.memory_set)
        valid       = False   # set to true if True
        correct     = False   # correct response or not: set to True if True
        rt          = -100    # -100 indicates no response; set to RT at runtime

    def run(self):
        # runs the trial, collects and analyzes the responses
        fixation_cross()
        display_memory_set(self.memory_set)
        pygame.event.clear() # clear all events from the queue
        display_probe(self.probe)
        [response, self.rt, self.valid] = get_response()
        if not(self.valid):
            self.correct = False
        elif response == 'P' and self.target_present:
            self.correct = True
        elif response == 'A' and not(self.target_present):
            self.correct = True
        else:
            self.correct = False

def introduce_block():
    # gives the subject the chance to rest between blocks
    screen.fill((250,250,250))# GRAY)  # fill it with a very light gray...
    blit_text('At this point you can take a moment to rest.',5)
    blit_text('On each trial of the next block of trials, press P if the probe is in',7)
    blit_text('  the memory set and A if it is not.',8)
    blit_text("Press P or A when you're ready to begin the next block.",10)
    pygame.display.update()
    get_keypress()

def correlation(vector1, vector2, mean1, mean2):
    # computes the correlation coefficient between vectors 1 and 2
    # recall that the correlation is just the cosine of the angle of vectors
    # of difference scores
    #
    # before you even begin, make sure vectors 1 and 2 have te same dimensionality
    if len(vector1) == len(vector2):
        # all good: proceed to calculate correlation
        # first, make the vectors of difference scores
        dot_product = 0 # dot product of diff vector1 with diff vector2
        len_vect1   = 0
        len_vect2   = 0
        for i in xrange(len(vector1)):
            diff1 = vector1[i] - mean1
            diff2 = vector2[i] - mean2
            dot_product += diff1 * diff2 # update dot product
            len_vect1 += pow(diff1, 2)   # update vector1 length
            len_vect2 += pow(diff2, 2)   # update vector1 length
        # now take sqrt of current length values
        len_vect1 = pow(len_vect1, 0.5)
        len_vect2 = pow(len_vect2, 0.5)
        # now coompute correlation as dot product divided by product of lengths
        if (len_vect1 * len_vect2) > 0:
            correlation = dot_product/(len_vect1 * len_vect2)
        else: correlation = 0
        return correlation
    else:
        print 'ERROR: You tried to calculate the correlation of two vectors of different lengths'
        print 'Length of vector 1 =',str(len(vector1))
        print 'Length of vector 2 =',str(len(vector2))
        return 0

def end_experiment():
    # saves the data to file, etc.

##    # update the subject count file
##    subject_count_file = file('subject count.txt', 'w')
##    subject_count_file.write(str(subject_number))
##    subject_count_file.close()
    
    # open the data file
    # data_file_name = 'data/data_'+str(subject_number)+'.txt'  # define the data file name
    # new 9/2/08: Usae time as filename to give each subject a unique file name
    end_time = time()
    data_file_name = 'data/'+str(end_time)+'.txt'
    data_file = open(data_file_name,'w')                 # open the data file for reading

    # --------------------------
    # Raw Data
    # --------------------------
    # write file key, etc
    data_file.write('Data File: Memory Search Experiment.\n\n')
    data_file.write('Subject # '+data_file_name+'\n\n')
    data_file.write('Raw Data:\n\n')
    data_file.write('Block\tTrial\tProbe\tMemSet\tPresent\tCorrect\tRT\n\n')
    # print the raw data
    for block in blocks:
        for trial in block.trials:
            text_line = str(block.index)+'\t'+str(trial.order)+'\t'+trial.probe+'\t'
            text_line = text_line+trial.memory_set+'\t'
            if trial.target_present: present_text = '1\t'
            else: present_text = '0\t'
            text_line = text_line+present_text
            if trial.valid and trial.correct:
                correct_text = '1\t'
            else:
                correct_text = '0\t'
            rt_text = '%.4f' % trial.rt
            text_line = text_line+correct_text+rt_text+'\n' 
            data_file.write(text_line)

    # --------------------------
    # Summary Data
    # --------------------------
    data_file.write('\n\nSummary Data by Blocks:\n\n')
    data_file.write('Block\t\tAccuracy\t\t\t\tResponse Time (sec)\n')
    data_file.write('SetSize:\t1\t2\t3\t4\t5\t1\t2\t3\t4\t5\n\n')
    # calculate and save summary data by blocks and overall summary data
    # the following vectors are for calculating the correlation between set size and rt,
    #   which will be used to calculate the slope of the search function Overall
    overall_rt_present = []
    overall_rt_absent  = []
    overall_set_size_present = []
    overall_set_size_absent  = []
    # the following are for calculating rt and accuracy by set size overall
    overall_rt_by_set_size_present = [[],[],[],[],[]] # five vectors, one for each set size
    overall_rt_by_set_size_absent  = [[],[],[],[],[]] # five vectors, one for each set size
    overall_acc_by_set_size_present = [[],[],[],[],[]] # five vectors, one for each set size
    overall_acc_by_set_size_absent  = [[],[],[],[],[]] # five vectors, one for each set size
    # now get down to work
    for block in blocks:
        # the following vectors are for calculating the correlation between set size and rt,
        #   which will be used to calculate the slope of the search function for This block
        block_rt_present = []
        block_rt_absent  = []
        block_set_size_present = []
        block_set_size_absent  = []
        # the following are for calculating rt and accuracy by set size overall
        block_rt_by_set_size_present = [[],[],[],[],[]] # five vectors, one for each set size
        block_rt_by_set_size_absent  = [[],[],[],[],[]] # five vectors, one for each set size
        block_acc_by_set_size_present = [[],[],[],[],[]] # five vectors, one for each set size
        block_acc_by_set_size_absent  = [[],[],[],[],[]] # five vectors, one for each set size
        # do this block's data analysis
        for trial in block.trials:
            # get the set size
            set_size = len(trial.memory_set)
            # do all the stuff you have to do with data from correct trials
            if trial.correct:
                # target present data
                if trial.target_present:
                    # vectors for correlation calculation...
                    overall_rt_present.append(trial.rt)
                    overall_set_size_present.append(set_size)
                    block_rt_present.append(trial.rt)
                    block_set_size_present.append(set_size)
                    # vectors for by-set-size analysis
                    overall_rt_by_set_size_present[set_size-1].append(trial.rt)
                    overall_acc_by_set_size_present[set_size-1].append(1) # 1 for correct
                    block_rt_by_set_size_present[set_size-1].append(trial.rt)
                    block_acc_by_set_size_present[set_size-1].append(1) # 1 for correct
                # target absent data
                else:
                    # vectors for correlation calculation...
                    overall_rt_absent.append(trial.rt)
                    overall_set_size_absent.append(set_size)
                    block_rt_absent.append(trial.rt)
                    block_set_size_absent.append(set_size)
                    # vectors for by-set-size analysis
                    overall_rt_by_set_size_absent[set_size-1].append(trial.rt)
                    overall_acc_by_set_size_absent[set_size-1].append(1) # 1 for correct
                    block_rt_by_set_size_absent[set_size-1].append(trial.rt)
                    block_acc_by_set_size_absent[set_size-1].append(1) # 1 for correct
            # do all the stuff you have to do with data from incorrect trials
            else:
                # target present data
                if trial.target_present:
                    # vectors for by-set-size analysis: rt for correct trials only
                    overall_acc_by_set_size_present[set_size-1].append(0) # 0 for incorrect
                    block_acc_by_set_size_present[set_size-1].append(0) 
                # target absent data
                else:
                    # vectors for by-set-size analysis: rt for correct trials only
                    overall_acc_by_set_size_absent[set_size-1].append(0) # 0 for incorrect
                    block_acc_by_set_size_absent[set_size-1].append(0)
        # At this point, you've got all the data for this block sorted.
        # Now analyze it:
        #   compute mean and sd of accuracy and rt by set size and target present/absent
        #
        # target present data
        text_line = str(block.index)+') Present:\t'
        # calculate and prepare to write accuracy by set size
        for acc_vec in block_acc_by_set_size_present:
            # each accuracy vector is for one set size: indices 0...4 for sizes 1...5
            num_correct = 0
            for datum in acc_vec:
                num_correct += datum # datum will be 1 for correct & 0 for incorrect
            if len(acc_vec) > 0:
                accuracy = float(float(num_correct)/len(acc_vec))
            else:
                accuracy = 0.0
            # write this accuracy to file
            text_line = text_line+'%.4f\t' % accuracy
        # calculate and prepare to write rt by set size
        for rt_vec in block_rt_by_set_size_present:
            # each rt vector is for one set size: indices 0...4 for sizes 1...5
            [mean, sd] = mean_and_sd(rt_vec)
            text_line = text_line+'%.4f\t' % mean
            # text_line = text_line+'%.4f)\t' % sd
        # write the line of etxt
        data_file.write(text_line+'\n')
        #
        # target absent data
        text_line = str(block.index)+') Absent:\t'
        # calculate and prepare to write accuracy by set size
        for acc_vec in block_acc_by_set_size_absent:
            # each accuracy vector is for one set size: indices 0...4 for sizes 1...5
            num_correct = 0
            for datum in acc_vec:
                num_correct += datum # datum will be 1 for correct & 0 for incorrect
            if len(acc_vec) > 0:
                accuracy = float(float(num_correct)/len(acc_vec))
            else:
                accuracy = 0.0
            # write this accuracy to file
            text_line = text_line+'%.4f\t' % accuracy
        # calculate and prepare to write rt by set size
        for rt_vec in block_rt_by_set_size_absent:
            # each rt vector is for one set size: indices 0...4 for sizes 1...5
            [mean, sd] = mean_and_sd(rt_vec)
            text_line = text_line+'%.4f\t' % mean
            # text_line = text_line+'%.4f)\t' % sd
        # write the line of text
        data_file.write(text_line+'\n')
        
        # calculate and print the rt slopes for present & absent data
        #---------------------------------------------------
        #
        #   you're going to compute each subject's search slope in each condition
        #   then just do a t-test on the slopes to see whether they are different
        #
        #   the slope is calculated as the rise over the run:
        #      the mean rise over the mean run
        #
        #   OR on the more general case, the slope = r * (std. dev. of y)/(std. of x)
        #   in this case:
        #      r = correlation between rt & num distractors
        #      std. of y is std of RT
        #      std. of x is std of # distractors
        #
        #--------------------------------------------------

        # target present data
        # first get mean and sd for rt...
        [mean_rt, sd_rt] = mean_and_sd(block_rt_present)
        # ... and set size
        [mean_set_size, sd_set_size] = mean_and_sd(block_set_size_present)
        # and get their correlation
        corr = correlation(block_rt_present, block_set_size_present, mean_rt, mean_set_size)
        if sd_set_size > 0:
            slope = 1000 * corr * (sd_rt/sd_set_size)  # the "* 1000" is to convert sec/item to ms/item
        else:
            slope = 0
        # intercept = y - mx, i.e.,
        # mean_rt - slope * mean_set_size
        intercept = 1000 * mean_rt - slope * mean_set_size
        # and print to file
        text_line = 'Target present slope of RT in set size = %.2f ms/item; ' % slope
        text_line = text_line + 'intercept = %.2f ms\n' % intercept
        data_file.write(text_line)

        # target absent data
        # first get mean and sd for rt...
        [mean_rt, sd_rt] = mean_and_sd(block_rt_absent)
        # ... and set size
        [mean_set_size, sd_set_size] = mean_and_sd(block_set_size_absent)
        # and get their correlation
        corr = correlation(block_rt_absent, block_set_size_absent, mean_rt, mean_set_size)
        if sd_set_size > 0:
            slope = 1000 * corr * (sd_rt/sd_set_size)  # the "* 1000" is to convert sec/item to ms/item
        else:
            slope = 0
        intercept = 1000 * mean_rt - slope * mean_set_size
        # and print to file
        text_line = 'Target absent slope of RT in set size = %.2f ms/item; ' % slope
        text_line = text_line + 'intercept = %.2f ms\n\n' % intercept
        data_file.write(text_line)

    # now do the same analyses for the overall data:
    # 1) compute mean and sd of accuracy and rt by set size and target present/absent
    data_file.write('Overall Summary Data (averaged over blocks)\n\n')
    data_file.write('\t\tAccuracy\t\t\t\tResponse Time (sec)\n')
    data_file.write('SetSize:\t1\t2\t3\t4\t5\t1\t2\t3\t4\t5\n\n')
    # target present data
    text_line = 'Present:\t'
    # calculate and prepare to write accuracy by set size
    for acc_vec in overall_acc_by_set_size_present:
        # each accuracy vector is for one set size: indices 0...4 for sizes 1...5
        num_correct = 0
        for datum in acc_vec:
            num_correct += datum # datum will be 1 for correct & 0 for incorrect
        if len(acc_vec) > 0:
            accuracy = float(float(num_correct)/len(acc_vec))
        else:
            accuracy = 0.0
        # write this accuracy to file
        text_line = text_line+'%.4f\t' % accuracy
    # calculate and prepare to write rt by set size
    for rt_vec in overall_rt_by_set_size_present:
        # each rt vector is for one set size: indices 0...4 for sizes 1...5
        [mean, sd] = mean_and_sd(rt_vec)
        text_line = text_line+'%.4f\t' % mean
        # text_line = text_line+'%.4f)\t' % sd
    # write the line of text
    data_file.write(text_line+'\n')

    # target absent data
    text_line = 'Absent:\t'
    # calculate and prepare to write accuracy by set size
    for acc_vec in overall_acc_by_set_size_absent:
        # each accuracy vector is for one set size: indices 0...4 for sizes 1...5
        num_correct = 0
        for datum in acc_vec:
            num_correct += datum # datum will be 1 for correct & 0 for incorrect
        if len(acc_vec) > 0:
            accuracy = float(float(num_correct)/len(acc_vec))
        else:
            accuracy = 0.0
        # write this accuracy to file
        text_line = text_line+'%.4f\t' % accuracy
    # calculate and prepare to write rt by set size
    for rt_vec in overall_rt_by_set_size_absent:
        # each rt vector is for one set size: indices 0...4 for sizes 1...5
        [mean, sd] = mean_and_sd(rt_vec)
        text_line = text_line+'%.4f\t' % mean
        # text_line = text_line+'%.4f)\t' % sd
    # write the line of text
    data_file.write(text_line+'\n\n')

    # 2) compute slope of search function for target present/absent
    # target present data
    # first get mean and sd for rt...
    [mean_rt, sd_rt] = mean_and_sd(overall_rt_present)
    # ... and set size
    [mean_set_size, sd_set_size] = mean_and_sd(overall_set_size_present)
    # and get their correlation
    corr = correlation(overall_rt_present, overall_set_size_present, mean_rt, mean_set_size)
    if sd_set_size > 0:
        slope = 1000 * corr * (sd_rt/sd_set_size) # the "* 1000" is to convert sec/item to ms/item
    else:
        slope = 0
    intercept = 1000 * mean_rt - slope * mean_set_size
    # and print to file
    text_line = 'Target present slope of RT in set size = %.2f ms/item; ' % slope
    text_line = text_line + 'intercept = %.2f ms\n' % intercept
    data_file.write(text_line)

    # target absent data
    # first get mean and sd for rt...
    [mean_rt, sd_rt] = mean_and_sd(overall_rt_absent)
    # ... and set size
    [mean_set_size, sd_set_size] = mean_and_sd(overall_set_size_absent)
    # and get their correlation
    corr = correlation(overall_rt_absent, overall_set_size_absent, mean_rt, mean_set_size)
    if sd_set_size > 0:
        slope = 1000 * corr * (sd_rt/sd_set_size) # the "* 1000" is to convert sec/item to ms/item
    else:
        slope = 0
    intercept = 1000 * mean_rt - slope * mean_set_size
    # and print to file
    text_line = 'Target absent slope of RT in set size = %.2f ms/item; ' % slope
    text_line = text_line + 'intercept = %.2f ms\n' % intercept
    data_file.write(text_line)
           
    # close the data file
    data_file.close()

    # inform the subject of end of experiment
    # first blank the screen and print the end-of-experiment message
    screen.fill((250,250,250))# GRAY)  # fill it with a middle gray...
    #
    blit_text('End of experiment.  Enter ctrl-F6 in the python shell to close this window.',10)
    # and update the screen
    pygame.display.update()



# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                               MAIN BODY
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#-----------------------------------------------
# Introduction
#-----------------------------------------------
# blank the screen
screen.fill((250,250,250))# GRAY)  # fill it with a middle gray...
blit_text('This experiment investigates how people search through memory.',1)
blit_text('On each trial, you will see an array of blue letters displayed on the screen.',3)
blit_text('After a brief delay, the array will disappear and a single black probe letter will',5)
blit_text('  appear on the screen.',6)
blit_text('If the probe was present in the array, press the P key; if it was not present',8)
blit_text('   in the array, press the A key (for "absent").',9)
blit_text('Please respond to each probe as quickly and accurately as you can.',11)
blit_text('Each trial will begin with a fixation cross in the center of the screen,',13)
blit_text('   followed by the array of letters and then by the probe.',14)
blit_text('Please keep your eyes fixated on this cross until the array of letters appears.',16)
blit_text('Press P or A to continue to a few practice trials.',18) # John: Line 20 is the last line
# finally, update the screen
pygame.display.update()

get_keypress()

# -----------------------------------
# Practice trials
# -----------------------------------
#
practice = []
for i in xrange(4): # four practice trials
    set_size = 1 + int(round(random.random() * 3)) #  set size = 1...4
    # make two target present trials, two target absent
    if i < 2:
        target_present = True
    else:
        target_present = False
    # make the trial
    practice.append(Trial(practice, set_size, target_present))
# randomize the trial order
shuffle(practice)
# & present the practice trials
for trial in practice:
    trial.run()

# -----------------------------------
# Start the experiment
# -----------------------------------
#
# ready screen
screen.fill((250,250,250))# GRAY)  # fill it with a very light gray...
blit_text('Now get ready for the real experiment.',7)
blit_text('Remember to respond as quickly as you can Without Making Mistakes.',9)
blit_text('Place your fingers above the A and P keys...',11)
blit_text('... and press P or A to begin the experiment.',12)
pygame.display.update()
get_keypress()

# set up the blocks/conditions
# 10 blocks of 40 trials each
# each trial presents four present and four absent trials of each memory set size: 1...5
num_blocks = 5 # 5 # change to 5 for real experiment
blocks = []
for i in xrange(num_blocks):
    # make the block
    blocks.append(Block(i))
    # get the last block
    block = blocks[-1]
    # make the trials
    for ss_index in xrange(5):
        set_size = ss_index + 1 # set sizes 1...5
        # now four target present and four target absent of this set_size
        for j in xrange(4):  # change to 4 for real experiment
            block.trials.append(Trial(block, set_size, True)) # target present
            block.trials.append(Trial(block, set_size, False)) # target absent
    # randomize the trials' order
    shuffle(block.trials)
    # calculate each trial's index
    t_index = 0
    for trial in block.trials:
        t_index += 1
        trial.order = t_index

# -----------------------------------
# now run the blocks!
# -----------------------------------
for block in blocks:
    introduce_block()
    for trial in block.trials:
        trial.run()

           
# finally, end the experiment: save data, close files, etc.        
end_experiment()

# goodbye message
screen.fill((250,250,250))# GRAY)  # fill it with a middle gray...
blit_text('All done.',5)
blit_text('Press any key to quit the experiment.',7)
pygame.display.update()
get_keypress()
# close the screen
pygame.display.quit()

