#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2010,2011  Roland Arsenault

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import gpsvideo


def extract(args,output):
    global_outfile = None
    if args.out is not None:
        global_outfile = open(args.out,'wt')
        output.append_output('output: '+args.out)
    for a in args.infiles:
        qt = gpsvideo.qt.QTFile(a)
        output.append_output('input: '+a)
        if global_outfile is not None:
            outfile = global_outfile
        else:
            outfile = open(a+'.nmea','wt')
            output.append_output('output: '+a+'.nmea')
        #qt.Print()
        tracks = qt.find('moov')[0][1].find('trak')
        text_tracks = []
        for t in tracks:
            if t[1].find('mdia')[0][1].find('hdlr')[0][1].componentSubType == b'text':
                #t[1].Print('')
                sc = gpsvideo.qt.SampleCursor(t[1])
                s = sc.nextSample()
                tid = t[1].find('tkhd')[0][1].trackID
                ts = t[1].find('mdia')[0][1].find('mdhd')[0][1].timeScale
                text_tracks.append([tid,sc,s,ts])

        done = False
        while not done:
            nextSampleTime = None

            for tt in text_tracks:
                if tt[2] is not None:
                    if nextSampleTime is None:
                        nextSampleTime = tt[2][0]
                    else:
                        if tt[2][0] < nextSampleTime:
                            nextSampleTime = tt[2][0]

            if nextSampleTime is not None:
                for tt in text_tracks:
                    if tt[2] is not None:
                        if tt[2][0] == nextSampleTime:
                            lines = tt[2][1].decode('utf_8','ignore').split()
                            for l in lines:
                                if args.debug:
                                    nmea = l
                                else:
                                    nmea = gpsvideo.nmea.FindNmea(l)
                                if nmea is not None:
                                    if args.timestamp:
                                        outfile.write(str(nextSampleTime/float(tt[3]))+',')
                                    outfile.write(nmea+'\n')
                            tt[2] = tt[1].nextSample()

            done = True
            for tt in text_tracks:
                if tt[2] is not None:
                    done = False
    output.append_output('done')
    
class StdPrint:
    def append_output(self,text):
        print (text)
                    
def CommandLine():
    import argparse

    parser = argparse.ArgumentParser(description='Extract GPS data from mov files.',
                                     epilog='If no output file is specified, an output file is created for each input file by appending .nmea to the input filename.')
                                     
    parser.add_argument('infiles',
                        metavar='infile.mov',
                        nargs='+',
                        help='input mov files')
                        
    parser.add_argument('--ts','-t',
                        dest='timestamp',
                        action='store_true',
                        default = False,
                        help='include timestamps in output')
                        
    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        default = False,
                        help='extracts all text found in subtitles instead of just nmea strings')
                        
    parser.add_argument('--out','-o',
                        dest='out',
                        nargs='?',
                        default=None,
                        help='If specified, output file in which data from all input files will be saved')
                        
    args = parser.parse_args()
    extract(args,StdPrint())

class ArgsGui:
    def __init__(self, root):
        self.infiles = []
        self.timestamp = False
        self.debug = False
        self.out = None

        frame = Tkinter.Frame(root)
        frame.pack(expand=True,fill='both')

        in_frame = Tkinter.LabelFrame(frame,text='input')
        in_frame.pack(side="top",fill='x')

        self.in_text = Tkinter.Entry(in_frame)
        self.in_text.pack(side='left',expand=True,fill='x')

        in_button = Tkinter.Button(in_frame, text="...", command=self.choose_infile)
        in_button.pack(side='left')

        out_frame = Tkinter.LabelFrame(frame,text='output')
        out_frame.pack(side="top",fill='x')
        
        self.out_text = Tkinter.Entry(out_frame)
        self.out_text.pack(side='left',expand=True,fill='x')
        
        out_button = Tkinter.Button(out_frame, text="...", command=self.choose_outfile)
        out_button.pack(side='right')

        opts_frame = Tkinter.Frame(frame)
        opts_frame.pack(side='top',fill='x')

        self.ts_var = Tkinter.IntVar()
        ts_check = Tkinter.Checkbutton(opts_frame,text='timestamps',variable=self.ts_var)
        ts_check.pack(side='left')

        self.debug_var = Tkinter.IntVar()
        debug_check = Tkinter.Checkbutton(opts_frame,text='debug',variable=self.debug_var)
        debug_check.pack(side='left')
        
        extract_button = Tkinter.Button(opts_frame, text="Extract", command=self.do_extract)
        extract_button.pack(side='right')

        self.output_text = ScrolledText.ScrolledText(frame)
        self.output_text.pack(side='top',fill='both',expand=True)
        self.append_output('mov2nmea')
        self.append_output('For command line usage, launch with -h or --help')
        
        
    def append_output(self,text):
        self.output_text.config(state='normal')
        self.output_text.insert('end',text+'\n')
        self.output_text.config(state='disabled')
        
    def choose_infile(self):
        fname = tkFileDialog.askopenfilename()
        if len(fname):
            self.in_text.delete(0,'end')
            self.in_text.insert('end',fname)

    def choose_outfile(self):
        fname = tkFileDialog.asksaveasfilename()
        if len(fname):
            self.out_text.delete(0,'end')
            self.out_text.insert('end',fname)
            
        
    def do_extract(self):
        infile = self.in_text.get()
        outfile = self.out_text.get()
        if len(infile):
            self.infiles = [infile]
            self.out = None
            if len(outfile):
                self.out = outfile
            self.timestamp = self.ts_var.get() == 1
            self.debug = self.debug_var.get() == 1
            extract(self,self)
        else:
            self.append_output('missing input file')
        
def Gui():
    print('Launching gui, for command line usage, launch with -h or --help')

    root = Tkinter.Tk()
    root.title('mov2nmea')
    app = ArgsGui(root)
    root.mainloop()

    
if len(sys.argv) < 2:
    import Tkinter
    import ScrolledText
    import tkFileDialog
    Gui()
else:
    CommandLine()

