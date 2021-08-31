# -*- coding: utf-8 -*-

from tkinter import *
import Pmw
from tkinter import filedialog

import locale
encoding = locale.getdefaultlocale()[1]
import codecs

import os

root = Tk()
#root.option_readfile('optionDB')
root.option_add('*font', (u'simsung', '10', ''))#verdana， courier, simsung
root.title(u'Pig-ball Interaction Time Counter by Rui Wang, 2021-Apr-10')


# Data structure

# Last movement
last_movement = [ # keyOfDict, clock_start
    ]
# Record for the current pig
last_record = [   # (direction, time_interver)
    ]

# All record
list_record = [   # (No,(total_counts, total_accumulations, touch_counts, touch_accumulations, leave_counts, leave_accumulations, others_counts, others_accumulations),
                  #     [direction, time_interver] )
    ]

# Clock when pausing
pause_start_clock = 0

# Time counter valid or not
isTimeCounter_Total_Valid = 0
isTimeCounter_ThisRec_Valid = 0

# Var for frame components
recordNo = IntVar()

touch_counts = IntVar()
touch_accumulations = IntVar()
leave_counts = IntVar()
leave_accumulations = IntVar()
others_counts = IntVar()
others_accumulations = IntVar()
total_counts = IntVar()
total_accumulations = IntVar()

saved_file = StringVar()

# Icons
dict_image = {
    'Up':     ['Up',      'touch.png',   None],
    'Down':   ['Down',    'leave.png',  None],
    'Left':   ['Left',    'others.png',    None],
    'Escape':  ['Escape',   'pause.png',     None],
    'Next':   ['Next',    'preparing.png', None],
    'Delete': ['Delete',  'delete.png',    None],
    }

#
def print_report(textbox, rpt): #Pmw.ScrolledText
    textbox.yview(END)
    textbox.insert(END, rpt)

def print_key_event(event_keysym, time, key):
    rpt = '\n%-10s%-10s%-10s' % (time, event_keysym, key[1])
    print_report(text_intime, rpt)

def key_Invalid(event_keysym, time, key):
    print_key_event(event_keysym, time, key)
    
def key_Delete(event_keysym, time, key):
    global last_movement, isTimeCounter_Total_Valid, isTimeCounter_ThisRec_Valid

    redraw_label(key[0])

    if len(last_movement) != 0:
        last_movement = []
        rpt = u'\nDelete the last movement'
    else:
        rpt = u'\nLast movement deleted or not exist, not delete at all'

    isTimeCounter_Total_Valid = 0
    isTimeCounter_ThisRec_Valid = 0
    timecounter_thisRec.setvalue('00:00:00')

    print_report(text_intime, rpt)

# Entry to this function if Pause key is pressed or any other key is pressed when pausing
def key_Pause(event_keysym, time, key):
    global pause_start_clock, last_movement, isTimeCounter_Total_Valid, isTimeCounter_ThisRec_Valid

    redraw_label('Escape')

    if pause_start_clock == 0: # Pausing
        pause_start_clock = time
        rpt = u'\nPause the counting for the current movement'
        isTimeCounter_Total_Valid = 0
        isTimeCounter_ThisRec_Valid = 0
    
    elif event_keysym != 'Escape': # non Pause key is pressed when pausing
        rpt = u'\nPausing...Press any key to exit pausing'
    
    else: # Exit pausing
        if len(last_movement) != 0:
            last_movement[1] = time-(pause_start_clock-last_movement[1])
            rpt = u'\nExit pausing, resume the counting for the last movement'
        else:
            rpt = u'\nExit pausing'
        pause_start_clock = 0
        isTimeCounter_Total_Valid = 1
        isTimeCounter_ThisRec_Valid = 1

    print_report(text_intime, rpt)

def key_Movement(event_keysym, time, key):
    global last_movement, last_record, isTimeCounter_Total_Valid, isTimeCounter_ThisRec_Valid

    isTimeCounter_Total_Valid = 1
    isTimeCounter_ThisRec_Valid = 1
        
    redraw_label(key[0])

    if len(last_movement) != 0:
        timecounter_thisRec.setvalue('00:00:00')
        # Calculate the statistics of the last movement, update data and refresh the interface
        last_record.append((dict_key[last_movement[0]][1], time-last_movement[1]))
        dict_key[last_movement[0]][3].set(1+dict_key[last_movement[0]][3].get())
        dict_key[last_movement[0]][4].set(time-last_movement[1]+dict_key[last_movement[0]][4].get())
        total_counts.set(1+total_counts.get())
        total_accumulations.set(time-last_movement[1]+total_accumulations.get())

    last_movement = [key[0], time]

    print_key_event(event_keysym, time, key)

def key_Next(event_keysym, time, key):
    global last_movement, last_record, list_record, isTimeCounter_Total_Valid, isTimeCounter_ThisRec_Valid

    isTimeCounter_Total_Valid = 0
    timecounter_total.setvalue('00:00:00')
    isTimeCounter_ThisRec_Valid = 0
    timecounter_thisRec.setvalue('00:00:00')

    redraw_label(key[0])

    if len(last_movement) != 0:
        # Calculate the statistics of the last movement, update data and refresh the interface
        last_record.append((dict_key[last_movement[0]][1], time-last_movement[1]))
        dict_key[last_movement[0]][3].set(1+dict_key[last_movement[0]][3].get())
        dict_key[last_movement[0]][4].set(time-last_movement[1]+dict_key[last_movement[0]][4].get())
        total_counts.set(1+total_counts.get())
        total_accumulations.set(time-last_movement[1]+total_accumulations.get())
    elif len(last_record) == 0:
        rpt = u'\nNo movement for the current number of pig is recorded; Number will not be added'
        print_report(text_intime, rpt)
        return

    # Stop recording for the current number of pig, reset data and interface
    list_record.append((
        recordNo.get(), (total_counts.get(), total_accumulations.get(),
        touch_counts.get(), touch_accumulations.get(), leave_counts.get(),
        leave_accumulations.get(), others_counts.get(), others_accumulations.get()),
        last_record[:]
        ))

    last_record=[]
    last_movement=[]

    recordNo.set(1+recordNo.get())
    touch_counts.set(0)
    touch_accumulations.set(0)
    leave_counts.set(0)
    leave_accumulations.set(0)
    others_counts.set(0)
    others_accumulations.set(0)
    total_counts.set(0)
    total_accumulations.set(0)
    
    print_key_event(event_keysym, time, key)

    # Print the recording of the current number of pig to screen
    rpt = u'\nRecord No.%s\n' % list_record[-1][0]
    rpt += '='*24 + '\n'
    rpt += u'Total times:%10s\nTotal duration:%6s\nTouch times:%10s\nTouch duration:%6s\
    \nLeave times:%10s\nLeave duration:%6s\nRest times:%10s\nRest duration:%6s\n' % \
    list_record[-1][1]
    rpt += '='*24 + '\n'
    for item in list_record[-1][2]:
        rpt += '%-10s%6s\n' % (item[0], item[1])
    rpt += '='*24 + '\n'
    print_report(text_output, rpt)

def load_image():
    global dict_image
    for v in dict_image.values():
        v[2] = PhotoImage(file=v[1])

def redraw_label(image_index):
    global dict_image
    label_image.configure(image=dict_image[image_index][2])
        

# Data dictionary for keys
dict_key   = {
    'Up':     ['Up',      u'Touch',                 key_Movement, touch_counts,  touch_accumulations],
    'Down':   ['Down',    u'Leave',                 key_Movement, leave_counts, leave_accumulations],
    'Left':   ['Left',    u'Rest',                 key_Movement, others_counts,   others_accumulations],
    'Escape':  ['Escape',   u'Pause',                 key_Pause],
    'Next':   ['Next',    u'Next', key_Next],
    'Delete': ['Delete',  u'Delete',              key_Delete],
    'INVALID':['INVALID', u'Invalid',             key_Invalid]
    }

# Resuming function for frame components
def keyEvent(event):
    global pause_start_clock

    key = dict_key.get(event.keysym, dict_key['INVALID'])

    if event.keysym == 'Right': # Right key=Left key
        key = dict_key['Left']

    if pause_start_clock > 0: # If pausing
        key_Pause(event.keysym, event.time, key)
        return

    # Resuming the functions for keys
    key[2](event.keysym, event.time, key)

def resumeEvent(event): # Recording button gets focus again
    btn_detect.focus_set()
    
def timecounter_total_update():
    if isTimeCounter_Total_Valid:
        timecounter_total.increment()
    timecounter_total.after(1000, timecounter_total_update)#update
    
def timecounter_thisRec_update():
    if isTimeCounter_ThisRec_Valid:
        timecounter_thisRec.increment()
    timecounter_thisRec.after(1000, timecounter_thisRec_update)#update

def selectFileName():
    ofile = filedialog.asksaveasfilename(filetypes=[(u'add.csv extension automatically','*')])
    if ofile: saved_file.set(ofile.rstrip('.csv'))#strip.csv

# Output to CSV file
def doSave_(ofile):
    fd1 = codecs.open(ofile+'.csv', 'w', encoding)
    fd2 = codecs.open(ofile+'_detail.csv', 'w', encoding)

    rpt = u'No., Total times, Total duration, Touch times, Touch duration, Leave times, Leave duration, Rest times, Rest duration\r\n'
    for rec in list_record:
        rpt += '%s, ' % rec[0]
        for item in rec[1][:-1]:
            rpt += '%s, ' % item
        rpt += '%s\r\n' % rec[1][-1]
    fd1.write(rpt)

    rpt = u'No., Movement, Duration\r\n'
    for rec in list_record:
        for item in rec[2]:
            rpt += '%s, ' % rec[0]
            rpt += '%s, %s\r\n' % (item[0], item[1])
    fd2.write(rpt)
    
    fd1.close()
    fd2.close()

def save2File():
    global list_record

    ofile = saved_file.get()
    if ofile == '': ofile = filedialog.asksaveasfilename(filetypes=[(u'add extension .csv','*')])
    if ofile == '': return
    else:
        ofile = ofile.rstrip('.csv')#strip.csv
        saved_file.set(ofile)

    doSave_(ofile)
    
    rpt = u'\nOK, saved!'
    print_report(text_intime, rpt)

def beforeQuit(event):

    dialog = Pmw.Dialog(root, buttons=('OK','Cancel'), defaultbutton='OK', title=u'Saving reminder！')
    Label(dialog.interior(), text=u'Choose a file name to save the current recording before exit,.csv not required\nCurrent folder is:')\
                             .pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)
    Label(dialog.interior(), text=(os.getcwd(), encoding))\
                             .pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)
    entry_fname = Entry(dialog.interior(), textvariable=saved_file)\
                            .pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)
    ret = dialog.activate()

    ofile = saved_file.get()
    
    if ofile == '' or ret != 'OK': return

    doSave_(ofile)

# Frame components
# main_frame
main_frame = Frame(root, takefocus=1, highlightthickness=1)
main_frame.pack(fill=BOTH, expand=YES)
main_frame.bind('<Destroy>', beforeQuit)#Event bound
# in root->main_frame
frame_top = Frame(main_frame)
frame_body = Frame(main_frame)
frame_bottom = Frame(main_frame)
# pack
frame_top.pack(side=TOP, fill=X, padx=5, pady=5)
frame_body.pack(side=TOP, fill=BOTH, expand=YES, padx=5, pady=5)
frame_bottom.pack(side=TOP, fill=X, padx=5, pady=5)

# in main_frame->frame_top
text_recordNo = Pmw.Counter(frame_top, labelpos=W, label_text=u'Pig Number',\
                            entry_width=4, entryfield_entry_textvariable=recordNo, entryfield_value=1, \
                            entryfield_validate={'validator':'integer', 'min':1, 'max':9999})#Var bound and initialized
btn_detect = Button(frame_top, takefocus=1, text=u'Begin recording', \
                    borderwidth=2, relief=RIDGE, bg='#0000FF', fg='#FFFF00')
btn_detect.bind('<KeyPress>', keyEvent)#Event bound
btn_detect.bind('<Button-1>', resumeEvent)#Event bound
# pack
btn_detect.pack(side=RIGHT, padx=5, pady=5)
text_recordNo.pack(side=RIGHT, padx=5, pady=5)

# in main_frame->frame_body
frame_statistics = Frame(frame_body, takefocus=1, borderwidth=1, relief=GROOVE)
text_intime = Pmw.ScrolledText(frame_body, text_width=40, text_height=6)
# pack
frame_statistics.pack(side=LEFT, padx=5, pady=5, fill=BOTH, expand=YES)
text_intime.pack(side=LEFT, padx=5, pady=5, fill=BOTH, expand=YES)

# in frame_body->frame_statistics
frame_statistics_top = Frame(frame_statistics)
text_output = Pmw.ScrolledText(frame_statistics, text_width=30, text_height=6)
# pack
frame_statistics_top.pack(side=TOP, padx=5, pady=5)
text_output.pack(side=TOP, padx=5, pady=5, fill=BOTH, expand=YES)

# in frame_statistics->frame_statistics_top
label_movement = Label(frame_statistics_top, text=u'Movement')
label_counts = Label(frame_statistics_top, text=u'Time')
label_accumulation = Label(frame_statistics_top, text=u'Duration(ms)')

label_touch = Label(frame_statistics_top, text=u'Touch:')
text_touch_counts = Entry(frame_statistics_top, textvariable=touch_counts, width=8)#Var bound
text_touch_accumulations = Entry(frame_statistics_top, textvariable=touch_accumulations, width=8)#Var bound

label_leave = Label(frame_statistics_top, text=u'Leave:')
text_leave_counts = Entry(frame_statistics_top, textvariable=leave_counts, width=8)#Var bound
text_leave_accumulations = Entry(frame_statistics_top, textvariable=leave_accumulations, width=8)#Var bound

label_others = Label(frame_statistics_top, text=u'Rest:')
text_others_counts = Entry(frame_statistics_top, textvariable=others_counts, width=8)#Var bound
text_others_accumulations = Entry(frame_statistics_top, textvariable=others_accumulations, width=8)#Var bound

label_total = Label(frame_statistics_top, text=u'Sum:')
text_total_counts = Entry(frame_statistics_top, textvariable=total_counts, width=8)#Var bound
text_total_accumulations = Entry(frame_statistics_top, textvariable=total_accumulations, width=8)#Var bound

label_image = Label(frame_statistics_top, text=u'Icons', width=48, height=48, relief=RIDGE, borderwidth=1)
timecounter_total = Pmw.TimeCounter(frame_statistics_top, label_text=u'Current Pig No.', labelpos=NW,
                                    min='00:00:00', max='23:59:59', value='00:00:00')
timecounter_thisRec = Pmw.TimeCounter(frame_statistics_top, label_text=u'Current Movement', labelpos=NW,
                                    min='00:00:00', max='23:59:59', value='00:00:00')

# grid
label_movement.grid(row=0, column=0, sticky=EW)
label_counts.grid(row=0, column=1, sticky=EW)
label_accumulation.grid(row=0, column=2, sticky=EW)

label_touch.grid(row=1, column=0, sticky=EW)
text_touch_counts.grid(row=1, column=1, sticky=EW)
text_touch_accumulations.grid(row=1, column=2, sticky=EW)

label_leave.grid(row=2, column=0, sticky=EW)
text_leave_counts.grid(row=2, column=1, sticky=EW)
text_leave_accumulations.grid(row=2, column=2, sticky=EW)

label_others.grid(row=3, column=0, sticky=EW)
text_others_counts.grid(row=3, column=1, sticky=EW)
text_others_accumulations.grid(row=3, column=2, sticky=EW)

label_total.grid(row=4, column=0, sticky=EW)
text_total_counts.grid(row=4, column=1, sticky=EW)
text_total_accumulations.grid(row=4, column=2, sticky=EW)

label_image.grid(row=5, column=0, sticky=W)
timecounter_total.grid(row=5, column=1, sticky=W, padx=5, pady=5)
timecounter_thisRec.grid(row=5, column=2, sticky=W, padx=5, pady=5)

# in main_frame->frame_bottom
text_saved_file = Entry(frame_bottom, textvariable=saved_file, width=32)
btn_select_file = Button(frame_bottom, text=u'Choose a file to save', command=selectFileName)#Event bound
btn_save_file = Button(frame_bottom, text=u'Save', command=save2File)#Event bound
# pack
text_saved_file.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=X)
btn_select_file.pack(side=LEFT, padx=5, pady=5)
btn_save_file.pack(side=LEFT, padx=5, pady=5)

# Initialize
touch_counts.set(0)
touch_accumulations.set(0)
leave_counts.set(0)
leave_accumulations.set(0)
others_counts.set(0)
others_accumulations.set(0)

load_image()
redraw_label('Next')

timecounter_total_update()
timecounter_thisRec_update()

saved_file.set('')

print_report(text_output, u'Movement recording for current pig:\n')

btn_detect.focus_set()

# Mainloop
root.mainloop()
